import pyximport

pyximport.install(language_level='3')

import cv2
from glob import glob
from os.path import basename, dirname
import math

from core.logger import get_root_logger
from core.fileIO import create_folders, create_file, append_file, save_plot
from core.detection import detect_quadrilaterals, calculate_accuracy_metrics
from core.visualize import resize_image, show_image, draw_quadrilaterals_opencv
from data.imageRepo import get_paintings_for_image

logger = get_root_logger()


def run_task_02(dataset_folder='dataset_pictures_msk', show=True, save=True):
    if dataset_folder == 'dataset_pictures_msk' and save:
        filename = create_file('./results/task2/dataset_pictures_msk_detection')
        plot_filename_base = './results/task2/dataset_pictures_msk_'

    filenames = glob('./datasets/images/' + dataset_folder + '/zaal_*/*.jpg')

    false_negatives_sum = 0
    false_positives_sum = 0
    average_accuracy_sum = 0
    count = 0

    false_negatives_per_room = {}  # key -> room, value -> false negatives count
    false_positives_per_room = {}  # key -> room, value -> false positive count
    all_accuracies = {}  # key -> image filename, value -> accuracy
    all_accuracies_per_room = {}  # key -> room, value -> dictionary of tupples of sum of accuracies [0] and count of paintings in the room [1]
    all_accuracies_per_room_processed = {}  # key -> room, value -> average room accuracy
    per_10_accuracy_count = {}  # key -> upper perentage of range (eg. 10: 0-10), value -> counter
    per_10_accuracy_count_processed = {}  # key -> percentage range, value -> counter

    for f in filenames:
        original_image = cv2.imread(f, 1)

        filename_image = basename(f)
        room_name = basename(dirname(f)).replace('_', ' ')

        original_image = resize_image(original_image, 0.2)
        image = original_image.copy()
        ground_truth_paintings = get_paintings_for_image(basename(f))
        detected_paintings = detect_quadrilaterals(image)

        (image, paintings_found, false_negatives, false_positives, average_accuracy) = calculate_accuracy_metrics(image, ground_truth_paintings, detected_paintings)

        if dataset_folder == 'dataset_pictures_msk':
            if save:
                append_file(filename, f + '\n')

            log = "# of false negatives: {}".format(false_negatives)
            logger.info(log)
            if save:
                append_file(filename, log + '\n')

            log = "# of false positives: {}".format(false_positives)
            logger.info(log)
            if save:
                append_file(filename, log + '\n')

            log = "average bounding box accuracy: {}".format(average_accuracy)
            logger.info(log)
            if save:
                append_file(filename, log + '\n\n')

            false_negatives_sum += false_negatives
            false_positives_sum += false_positives
            average_accuracy_sum += average_accuracy
            count += 1

            if room_name in false_negatives_per_room:
                false_negatives_per_room[room_name] += false_negatives
            else:
                false_negatives_per_room[room_name] = false_negatives

            if room_name in false_positives_per_room:
                false_positives_per_room[room_name] += false_positives
            else:
                false_positives_per_room[room_name] = false_positives

            all_accuracies[filename_image] = average_accuracy

            if room_name in all_accuracies_per_room:
                all_accuracies_per_room[room_name] = (
                all_accuracies_per_room[room_name][0] + average_accuracy, all_accuracies_per_room[room_name][1] + 1)
            else:
                all_accuracies_per_room[room_name] = (average_accuracy, 1)

            upper_range_value = int(math.ceil(average_accuracy * 10.0)) * 10
            if upper_range_value == 0: upper_range_value = 10
            if upper_range_value in per_10_accuracy_count:
                per_10_accuracy_count[upper_range_value] += 1
            else:
                per_10_accuracy_count[upper_range_value] = 1

        detection_image = draw_quadrilaterals_opencv(image, detected_paintings)

        if show:
            show_image(f, detection_image)

        if save:
            path = './results/task2/' + dataset_folder + '/' + basename(f)
            create_folders(path)
            cv2.imwrite(path, detection_image)

    for room_name in all_accuracies_per_room:
        all_accuracies_per_room_processed[room_name] = all_accuracies_per_room[room_name][0] / \
                                                       all_accuracies_per_room[room_name][1]

    for upper_range_value in range(10, 110, 10):
        if upper_range_value not in per_10_accuracy_count:
            per_10_accuracy_count[upper_range_value] = 0

    for upper_range_value in per_10_accuracy_count:
        range_str = str(upper_range_value - 10) + "-" + str(upper_range_value)
        per_10_accuracy_count_processed[range_str] = per_10_accuracy_count[upper_range_value]

    if dataset_folder == 'dataset_pictures_msk':
        save_plot(
            {'false negatives': false_negatives_per_room, 'false positives': false_positives_per_room},
            'False negatives and false positives per room',
            plot_filename_base + 'false_negatives_and_positives_detected_per_room'
        )

        save_plot(
            {'paintings': per_10_accuracy_count_processed},
            'Detection accuracy ranges',
            plot_filename_base + 'per_10_detection_accuracy_count'
        )

        save_plot(
            {'accuracy': all_accuracies_per_room_processed},
            'Average room detection accuracy',
            plot_filename_base + 'average_room_detection_accuracies'
        )

        log = "SUMMARY"
        logger.info(log)
        if save:
            append_file(filename, log + '\n')

        log = "total # of false negatives: {}".format(false_negatives_sum)
        logger.info(log)
        if save:
            append_file(filename, log + '\n')

        log = "total # of false positives: {}".format(false_positives_sum)
        logger.info(log)
        if save:
            append_file(filename, log + '\n')

        log = "average bounding box accuracy: {}".format(average_accuracy_sum / count)
        logger.info(log)
        if save:
            append_file(filename, log)
