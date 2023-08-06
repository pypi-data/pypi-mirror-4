from django.conf.urls.defaults import include, patterns
from tastypie.api import Api

from job_runner.apps.job_runner.api import (
    GroupResource,
    JobResource,
    JobTemplateResource,
    KillRequestResource,
    ProjectResource,
    RunLogResource,
    RunResource,
    WorkerResource,
)


v1_api = Api(api_name='v1')
v1_api.register(GroupResource()),
v1_api.register(JobResource())
v1_api.register(JobTemplateResource())
v1_api.register(KillRequestResource())
v1_api.register(ProjectResource())
v1_api.register(RunLogResource())
v1_api.register(RunResource())
v1_api.register(WorkerResource())

urlpatterns = patterns(
    '',
    (r'', include(v1_api.urls)),
)
