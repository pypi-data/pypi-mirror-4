from django import dispatch


stored_callback = dispatch.Signal(
    providing_args=['callback_instance', 'model_instance'],
)

processed_callback = dispatch.Signal(
    providing_args=['callback_instance', 'model_instance'],
)

error_callback = dispatch.Signal(
    providing_args=['callback_instance', 'model_instance'],
)
