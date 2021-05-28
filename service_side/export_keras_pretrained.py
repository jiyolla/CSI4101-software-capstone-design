import tensorflow as tf

models = ['Xception', 'MobileNetV2', 'DenseNet121', 'DenseNet169', 'DenseNet201', 'NASNetMobile']

for model in models:
    loaded_model = eval(f'tf.keras.applications.{model}()')
    tf.saved_model.save(loaded_model, f'./models/{model}/1')
    loaded_model = None

