from django.conf.urls.defaults import url, patterns


urlpatterns = patterns(
    'lava_scheduler_app.views',
    url(r'^$',
        'index',
        name='lava.scheduler'),
    url(r'^reports$',
        'reports',
        name='lava.scheduler.reports'),
    url(r'^active_jobs_json$',
        'index_active_jobs_json',
        name='lava.scheduler.active_jobs_json'),
    url(r'^devices_json$',
        'index_devices_json',
        name='lava.scheduler.index_devices_json'),
    url(r'^alljobs$',
        'job_list',
        name='lava.scheduler.job.list'),
    url(r'^alljobs_json$',
        'alljobs_json',
        name='lava.scheduler.job.list_json'),
    url(r'^device_type/(?P<pk>[-_a-zA-Z0-9]+)$',
        'device_type_detail',
        name='lava.scheduler.device_type.detail'),
    url(r'^device_type_json$',
        'device_type_json',
        name='lava.scheduler.device_type.device_type_json'),
    url(r'^device_type/(?P<pk>[-_a-zA-Z0-9]+)/index_nodt_devices_json$',
        'index_nodt_devices_json',
        name='lava.scheduler.device_type.index_nodt_devices_json'),
    url(r'^alldevices$',
        'device_list',
        name='lava.scheduler.alldevices'),
    url(r'^device/(?P<pk>[-_a-zA-Z0-9]+)$',
        'device_detail',
        name='lava.scheduler.device.detail'),
    url(r'^device/(?P<pk>[-_a-zA-Z0-9]+)/recent_jobs_json$',
        'recent_jobs_json',
        name='lava.scheduler.device.recent_jobs_json'),
    url(r'^device/(?P<pk>[-_a-zA-Z0-9]+)/transition_json$',
        'transition_json',
        name='lava.scheduler.device.transition_json'),
    url(r'^device/(?P<pk>[-_a-zA-Z0-9]+)/maintenance$',
        'device_maintenance_mode',
        name='lava.scheduler.device.maintenance'),
    url(r'^device/(?P<pk>[-_a-zA-Z0-9]+)/looping$',
        'device_looping_mode',
        name='lava.scheduler.device.looping'),
    url(r'^device/(?P<pk>[-_a-zA-Z0-9]+)/online$',
        'device_online',
        name='lava.scheduler.device.online'),
    url(r'^labhealth/$',
        'lab_health',
        name='lava.scheduler.labhealth'),
    url(r'^labhealth/health_json$',
        'lab_health_json',
        name='lava.scheduler.labhealth_json'),
    url(r'^labhealth/device/(?P<pk>[-_a-zA-Z0-9]+)$',
        'health_job_list',
        name='lava.scheduler.labhealth.detail'),
    url(r'^labhealth/device/(?P<pk>[-_a-zA-Z0-9]+)/job_json$',
        'health_jobs_json',
        name='lava.scheduler.labhealth.health_jobs_json'),
    url(r'^job/(?P<pk>[0-9]+)$',
        'job_detail',
        name='lava.scheduler.job.detail'),
    url(r'^job/(?P<pk>[0-9]+)/definition$',
        'job_definition',
        name='lava.scheduler.job.definition'),
    url(r'^job/(?P<pk>[0-9]+)/definition/plain$',
            'job_definition_plain',
            name='lava.scheduler.job.definition.plain'),
    url(r'^job/(?P<pk>[0-9]+)/log_file$',
            'job_log_file',
            name='lava.scheduler.job.log_file'),
    url(r'^job/(?P<pk>[0-9]+)/log_file/plain$',
                'job_log_file_plain',
                name='lava.scheduler.job.log_file.plain'),
    url(r'^job/(?P<pk>[0-9]+)/cancel$',
        'job_cancel',
        name='lava.scheduler.job.cancel'),
    url(r'^job/(?P<pk>[0-9]+)/json$',
        'job_json',
        name='lava.scheduler.job.json'),
    url(r'^job/(?P<pk>[0-9]+)/output$',
        'job_output',
        name='lava.scheduler.job.output'),
    url(r'^job/(?P<pk>[0-9]+)/log_incremental$',
        'job_log_incremental',
        name='lava.scheduler.job.log_incremental'),
    url(r'^job/(?P<pk>[0-9]+)/full_log_incremental$',
        'job_full_log_incremental',
        name='lava.scheduler.job.full_log_incremental'),
    )
