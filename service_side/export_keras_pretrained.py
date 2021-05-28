import tensorflow as tf

pretrained_model = tf.keras.applications.Xception()
tf.saved_model.save(pretrained_model, './Xception/1')

pretrained_model = tf.keras.applications.ResNet50()
tf.saved_model.save(pretrained_model, './ResNet50/1')

pretrained_model = tf.keras.applications.ResNet50V2()
tf.saved_model.save(pretrained_model, './ResNet50V2/1')

pretrained_model = tf.keras.applications.InceptionV3()
tf.saved_model.save(pretrained_model, './InceptionV3/1')

pretrained_model = tf.keras.applications.MobileNet()
tf.saved_model.save(pretrained_model, './MobileNet/1')

pretrained_model = tf.keras.applications.MobileNetV2()
tf.saved_model.save(pretrained_model, './MobileNetV2/1')

pretrained_model = tf.keras.applications.DenseNet121()
tf.saved_model.save(pretrained_model, './DenseNet121/1')

pretrained_model = tf.keras.applications.DenseNet169()
tf.saved_model.save(pretrained_model, './DenseNet169/1')
"""
pretrained_model = tf.keras.applications.DenseNet201()
tf.saved_model.save(pretrained_model, './DenseNet201/1')

pretrained_model = tf.keras.applications.NASNetMobile()
tf.saved_model.save(pretrained_model, './NASNetMobile/1')

pretrained_model = tf.keras.applications.EfficientNetB0()
tf.saved_model.save(pretrained_model, './EfficientNetB0/1')

pretrained_model = tf.keras.applications.EfficientNetB1()
tf.saved_model.save(pretrained_model, './EfficientNetB1/1')

pretrained_model = tf.keras.applications.EfficientNetB2()
tf.saved_model.save(pretrained_model, './EfficientNetB2/1')

pretrained_model = tf.keras.applications.EfficientNetB3()
tf.saved_model.save(pretrained_model, './EfficientNetB3/1')

pretrained_model = tf.keras.applications.EfficientNetB4()
tf.saved_model.save(pretrained_model, './EfficientNetB4/1')
