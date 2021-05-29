models = ['Xception', 'InceptionV3', 'MobileNetV2', 'DenseNet121', 'DenseNet169', 'EfficientNetB0']


def main():
    export = __import__('export_keras_pretrained')
    with open('models.config', 'w') as f:
        f.write('model_config_list {')
        for model in models:
            export.main(model)
            f.write('    config {')
            f.write(f'        name: {model}')
            f.write(f'        base_path: "/models/{model}/"')
            f.write('model_platform: "tensorflow"')
            f.write('    }')
        f.write('}')


if __name__ == '__main__':
    main()
