import serverless_sdk
sdk = serverless_sdk.SDK(
    org_id='eyoo95',
    application_name='perform-server-aws',
    app_uid='zVj5D6sJCqtn4FG15h',
    org_uid='8a31466c-85ba-471f-ae1b-8be5217f922b',
    deployment_uid='c043937c-794f-4049-82f4-70fe68401aca',
    service_name='perform-server-aws',
    should_log_meta=True,
    should_compress_logs=True,
    disable_aws_spans=False,
    disable_http_spans=False,
    stage_name='dev',
    plugin_version='6.2.2',
    disable_frameworks_instrumentation=False,
    serverless_platform_stage='prod'
)
handler_wrapper_kwargs = {'function_name': 'perform-server-aws-dev-api', 'timeout': 6}
try:
    user_handler = serverless_sdk.get_user_handler('wsgi_handler.handler')
    handler = sdk.handler(user_handler, **handler_wrapper_kwargs)
except Exception as error:
    e = error
    def error_handler(event, context):
        raise e
    handler = sdk.handler(error_handler, **handler_wrapper_kwargs)
