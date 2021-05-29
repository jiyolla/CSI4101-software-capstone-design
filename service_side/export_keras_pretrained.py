import tensorflow as tf


models = ['Xception', 'InceptionV3', 'MobileNetV2', 'DenseNet121', 'DenseNet169', 'EfficientNetB0']


def main():
    with open('models.config', 'w') as f:
        f.write('model_config_list {')
        for model in models:
            print(f'Loading {model}...')
            loaded_model = eval(f'tf.keras.applications.{model}')
            tf.saved_model.save(loaded_model(), f'./models/{model}/1')
            f.write('    config {')
            f.write(f'        name: {model}')
            f.write(f'        base_path: "/models/{model}/"')
            f.write('model_platform: "tensorflow"')
            f.write('    }')
            print(f'{model} loaded.')
        f.write('}')


if __name__ == '__main__':
    main()
