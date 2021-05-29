import tensorflow as tf


def main(model):
    print(f'Loading {model}...')
    loaded_model = eval(f'tf.keras.applications.{model}')
    tf.saved_model.save(loaded_model(), f'./models/{model}/1')
    print(f'{model} loaded.')
