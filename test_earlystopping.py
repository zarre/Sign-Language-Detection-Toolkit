import unittest
from Training import SEED
from model import *
from extract_datapoints import count_videos
import linecache

#a requirement for this test is having training data extracted from video sources with 15 frames hands only
class TestEarlyStopping(unittest.TestCase):

    def test_earlystopping(self):
        # Arrange
        TEST_EPOCH_AMOUNT = 5000
        model = YubiModel(15,126,np.array(['A', 'B', 'C', 'D', 'E', 'Idle']), os.path.join('MP_Data'), is_test = True)

        # Act
        model.train_model(TEST_EPOCH_AMOUNT,count_videos('Training_videos', np.array(['A', 'B', 'C', 'D', 'E', 'Idle'])), SEED)
        line = linecache.getline(os.path.join(f'{model.logs_path}', "training_info.txt"), 3)
        actual_epoch = [int(s) for s in line.split() if s.isdigit()]

        # Assert
        self.assertLess(actual_epoch[0], TEST_EPOCH_AMOUNT)

if __name__ == '__main__':
    unittest.main()