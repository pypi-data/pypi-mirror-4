import json
import logging
import time
from datetime import datetime, timedelta

import zmq
from django.conf import settings
from django.core.management.base import NoArgsCommand

from job_runner.apps.job_runner.models import KillRequest, Run, Worker


logger = logging.getLogger(__name__)


class Command(NoArgsCommand):
    help = 'Broadcast runs and kill-requests to workers'

    def handle_noargs(self, **options):
        logger.info('Starting queue broadcaster')
        context = zmq.Context(1)
        publisher = context.socket(zmq.PUB)
        publisher.bind(
            'tcp://*:{0}'.format(settings.JOB_RUNNER_BROADCASTER_PORT))

        # give the subscribers some time to (re-)connect.
        time.sleep(2)

        ping_delta = timedelta(
            seconds=settings.JOB_RUNNER_WORKER_PING_INTERVAL)
        next_ping_request = datetime.utcnow()

        while True:
            if next_ping_request <= datetime.utcnow():
                self._broadcast_worker_ping(publisher)
                next_ping_request = datetime.utcnow() + ping_delta
            self._broadcast_runs(publisher)
            self._broadcast_kill_requests(publisher)
            time.sleep(5)

        publisher.close()
        context.term()

    def _broadcast_runs(self, publisher):
        """
        Broadcast runs that are scheduled to run now.

        When the job has ``job__enqueue_is_enabled`` set to ``False``, its
        runs are not broadcasted, unless they are scheduled manually
        (``is_manual`` set to ``True``).

        :param publisher:
            A ``zmq`` publisher.

        """
        enqueueable_runs = Run.objects.enqueueable().select_related()

        broadcasted_job_ids = []

        for run in enqueueable_runs:
            if run.job.pk not in broadcasted_job_ids:
                worker = run.job.job_template.worker
                message = [
                    'master.broadcast.{0}'.format(worker.api_key),
                    json.dumps({'run_id': run.id, 'action': 'enqueue'})
                ]
                logger.debug('Sending: {0}'.format(message))
                publisher.send_multipart(message)

                # in raw sql, this can be avoided, I couldn't find a way how
                # this can be done with the django orm
                broadcasted_job_ids.append(run.job.pk)

    def _broadcast_kill_requests(self, publisher):
        """
        Broadcast kill-requests.

        :param publisher:
            A ``zmq`` publisher.

        """
        kill_requests = KillRequest.objects.killable().select_related()

        for kill_request in kill_requests:
            run = kill_request.run
            worker = run.job.job_template.worker
            message = [
                'master.broadcast.{0}'.format(worker.api_key),
                json.dumps({
                    'kill_request_id': kill_request.id,
                    'action': 'kill',
                })
            ]
            logger.debug('Sending: {0}'.format(message))
            publisher.send_multipart(message)

    def _broadcast_worker_ping(self, publisher):
        """
        Broadcast ping-request to all the workers.

        :param publisher:
            A ``zmq`` publisher.

        """
        workers = Worker.objects.all()

        for worker in workers:
            message = [
                'master.broadcast.{0}'.format(worker.api_key),
                json.dumps({
                    'action': 'ping',
                })
            ]
            logger.debug('Sending: {0}'.format(message))
            publisher.send_multipart(message)
