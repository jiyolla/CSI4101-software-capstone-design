import sys
import os
import tensorflow as tf

sys.path.append(os.path.join(sys.path[0], '..'))
from common import available_models


def main():
    with open('models.config', 'w') as f:
        f.write('model_config_list {')
        for model in available_models.lst:
            print(f'Loading {model}...')
            loaded_model = eval(f'tf.keras.applications.{model}')
            tf.saved_model.save(loaded_model(), f'./models/{model}/1')
            print(f'{model} loaded.')
            f.write('    config {')
            f.write(f'        name: {model}')
            f.write(f'        base_path: "/models/{model}/"')
            f.write('model_platform: "tensorflow"')
            f.write('    }')
        f.write('}')


if __name__ == '__main__':
    main()
