"""ocr_data dataset."""
import os

import tensorflow_datasets as tfds


g_data_path = 'D:\\Users\\weibin.xu\\AppData\\Local\\Temp'
class Builder(tfds.core.GeneratorBasedBuilder):
  """DatasetBuilder for ocr_data dataset."""

  VERSION = tfds.core.Version('1.0.0')
  RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
  }

  def _info(self) -> tfds.core.DatasetInfo:
    """Returns the dataset metadata."""
    # TODO(ocr_data): Specifies the tfds.core.DatasetInfo object

    labels = []
    for file in os.listdir(os.path.join(g_data_path, "ocr_datas")):
        labels.append(self._get_filename(os.path.basename(file)))

    return self.dataset_info_from_configs(
        features=tfds.features.FeaturesDict({
            # These are the features of your dataset like images, labels ...
            'image': tfds.features.Image(shape=(40, 30, 3)),
            'label': tfds.features.ClassLabel(names=labels),
        }),
        # If there's a common (input, target) tuple from the
        # features, specify them here. They'll be used if
        # `as_supervised=True` in `builder.as_dataset`.
        supervised_keys=('image', 'label'),  # Set to `None` to disable
    )

  def _split_generators(self, dl_manager: tfds.download.DownloadManager):
    """Returns SplitGenerators."""
    # TODO(ocr_data): Downloads the data and defines the splits
    # path = dl_manager.download_and_extract('https://todo-data-url')

    # TODO(ocr_data): Returns the Dict[split names, Iterator[Key, Example]]
    tfds_path = tfds.core.Path(os.path.join(g_data_path, 'ocr_datas'))
    return {
        'train': tfds_path
    }

  def _generate_examples(self, path):
    """Yields examples."""
    # TODO(ocr_data): Yields (key, example) tuples from the dataset
    for file in path.glob('*.png'):
      yield 'key', {
          'image': file,
          'label': self._get_filename(os.path.basename(file)),
      }

  def _get_filename(self, filename):
      return filename[:filename.find('.')]