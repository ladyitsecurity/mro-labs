import matplotlib.pyplot as plt
import numpy as np

import lab1
import lab2


def get_euclidean_distance(x, y):
    x = x.reshape(2, )
    y = y.reshape(2, )
    return np.linalg.norm(x - y)
    # return distance.euclidean(x, y)


def show_samples(samples_array, colors_array):
    for samples, colors in zip(samples_array, colors_array):
        plt.scatter(samples[0, :], samples[1, :], color=colors)


def concatenate_samples(samples_array):
    result = samples_array[0]
    for i in range(1, len(samples_array)):
        result = np.concatenate((result, samples_array[i]), axis=1)
    return result


def find_first_center_and_max_distance(samples):
    samples_mean = np.mean(samples, axis=1)
    samples_mean = samples_mean.reshape(2, 1)
    distances = []
    for i in range(0, len(samples[1])):
        distances.append(get_euclidean_distance(samples_mean, samples[0:2, i]))
    m0 = np.argmax(distances)
    return samples[0:2, m0], distances[m0]


def find_second_center_and_max_distance(samples, m0):
    distances = []
    for i in range(0, len(samples[1])):
        distances.append(get_euclidean_distance(m0, samples[0:2, i]))
    m1 = np.argmax(distances)
    return samples[0:2, m1], distances[m1]


def remove_center_from_samples(samples, center):
    center = center.reshape(2, 1)
    copy = samples.copy()
    del_index = np.where(copy[0:2, :] == center)
    return np.delete(copy, del_index[1][1], axis=1)


def get_distances_to_centers(samples, centers_array):
    N = len(samples[1])
    distances = np.zeros(shape=(len(centers_array), N))
    for i in range(0, len(centers_array)):
        center = centers_array[i]
        for j in range(0, N):
            distances[i, j] = get_euclidean_distance(center, samples[0:2, j])
    return distances


def get_min_distances(min_indexes, distances_array):
    res = []
    for i in range(0, len(min_indexes)):
        res.append(distances_array[min_indexes[i], i])
    return np.array(res)


def get_sum_distance(distances_array):
    distance = 0
    for distances in distances_array:
        distance += sum(distances)
    return distance


def get_typical_distance(centers_array):
    center_distances = []
    i = 0
    for center in centers_array:
        center = center.reshape(2, 1)
        center_distances.append(get_distances_to_centers(center, centers_array))
        i += 1
    sum_distance = get_sum_distance(np.triu(center_distances))
    return 0.5 * sum_distance / len(center_distances)


def show_samples_with_min_indexes(samples, min_indexes, colors, centers):
    classes = [[] for _ in range(0, len(centers))]
    for i, cls in np.ndenumerate(min_indexes):
        classes[cls].append(samples[0:2, i])

    for k in range(0, len(centers)):
        classes[k] = np.array(classes[k])
    for class_, color in zip(classes, colors):
        shape = class_.shape
        new_shape = (shape[0], shape[1])
        class_ = np.reshape(class_, new_shape)
        class_ = np.transpose(class_)
        lab1.show_vector_points1(class_, color)

    plt.title(f'count centers = {len(centers)}')
    for c in centers:
        plt.scatter(c[0], c[1], marker='o', color='black', alpha=0.6, s=100)


def get_centres(samples):
    m0, m0_max_dist = find_first_center_and_max_distance(samples)
    m1, m1_max_dist = find_second_center_and_max_distance(samples, m0)
    centers_array = [m0, m1]
    remaining_samples = remove_center_from_samples(samples, m0)
    remaining_samples = remove_center_from_samples(remaining_samples, m1)
    max_distance_array = [m0_max_dist, m1_max_dist]
    t_distance_array = [0, 0]
    colors = ['red', 'green', 'blue', 'yellow', 'pink']
    while True:
        distances_array = get_distances_to_centers(remaining_samples, centers_array)
        min_indexes = np.argmin(distances_array, axis=0)
        show_samples_with_min_indexes(remaining_samples, min_indexes, colors, centers_array)
        plt.show()
        distances_array_min = get_min_distances(min_indexes, distances_array)
        max_indexes = np.argmax(distances_array_min)
        max_distance_array.append(distances_array_min[max_indexes])
        centers_candidate = remaining_samples[0:2, max_indexes]
        typical_distance = get_typical_distance(np.array(centers_array))
        t_distance_array.append(typical_distance)
        tmp_center_candidate = centers_candidate.reshape(2, 1)
        distances_array_from_centers = get_distances_to_centers(tmp_center_candidate, centers_array)
        d_min_index = np.argmin(distances_array_from_centers)
        d_min = distances_array_from_centers[d_min_index]
        if d_min < typical_distance:
            break
        centers_array.append(centers_candidate)
        remaining_samples = remove_center_from_samples(samples, centers_candidate)
    return centers_array, max_distance_array, t_distance_array


def get_s(samples, min_indexes, K):
    classes = [[] for _ in range(K)]
    for i, cls in np.ndenumerate(min_indexes):
        classes[cls].append(samples[0:2, i])

    for k in range(K):
        classes[k] = np.array(classes[k])

    return classes


def show_classes(classes, colors, centers):
    for class_, color in zip(classes, colors):
        shape = class_.shape
        new_shape = (shape[0], shape[1])
        class_ = np.reshape(class_, new_shape)
        class_ = np.transpose(class_)
        lab1.show_vector_points1(class_, color)
    for c in centers:
        plt.scatter(c[0], c[1], marker='o', color='black', alpha=0.6, s=100)


def k_means_method(samples, K, indexes_clusters=None):
    centers = []
    if indexes_clusters is not None:
        for index in indexes_clusters:
            centers.append(samples[0:2, index])
    else:
        for k in range(0, K):
            centers.append(samples[0:2, k])
    iter = 0
    stats_num_changed = []
    classes = None
    colors = ['red', 'green', 'blue', 'yellow', 'pink']
    while True:
        old_classes = classes
        distances = get_distances_to_centers(samples, centers)
        min_indexes = np.argmin(distances, axis=0)
        classes = get_s(samples, min_indexes, K)
        show_classes(classes, colors, centers)
        plt.title(f'iteration number: {iter}')
        iter += 1
        plt.show()
        changed = False

        if old_classes is not None:
            cur_changed = 0
            for i in range(K):
                for j in range(len(classes[i])):
                    if classes[i][j] not in old_classes[i]:
                        cur_changed += 1
            stats_num_changed.append(cur_changed)

        for i in range(K):
            new_center = classes[i].mean(axis=0)
            if not np.array_equal(new_center, centers[i]):
                changed = True
            centers[i] = new_center

        if not changed:
            break
    return centers, classes, stats_num_changed


if __name__ == '__main__':
    N = 50
    M1 = np.array([1, -1]).reshape(2, 1)
    M2 = np.array([2, 2]).reshape(2, 1)
    M3 = np.array([-1, 1]).reshape(2, 1)
    M4 = np.array([1, 1]).reshape(2, 1)
    M5 = np.array([-1, -1]).reshape(2, 1)
    M = [M1, M2, M3, M4, M5]
    B0 = np.array([[0.03, 0.01], [0.01, 0.02]])
    B1 = np.array([[0.02, -0.01], [-0.01, 0.03]])
    B2 = np.array([[0.015, 0.015], [0.015, 0.02]])
    B3 = np.array([[0.04, 0.0], [0.0, 0.03]])
    B4 = np.array([[0.01, -0.01], [-0.01, 0.015]])
    B = [B0, B1, B2, B3, B4]
    # samples1 = get_training_samples(M[0], B[0], 50)
    # samples2 = get_training_samples(M[1], B[1], 50)
    # samples3 = get_training_samples(M[2], B[2], 50)
    # samples4 = get_training_samples(M[3], B[3], 50)
    # samples5 = get_training_samples(M[4], B[4], 50)
    samples1, samples2, samples3, samples4, samples5 = lab2.load_features('five_classes.npy')
    colors_array = ['red', 'green', 'blue', 'pink', 'yellow']
    show_samples([samples1, samples2, samples3, samples4, samples5], colors_array)
    plt.show()

    # samples_array = [samples1, samples2, samples3, samples4, samples5]
    # samples_array_result = concatenate_samples(samples_array)
    # plt.title(f'minmax for 5 classes')
    # res = samples_array_result
    # m_array, max_dist_array, t_dist_array = get_centres(res)
    # fig = plt.figure(figsize=(12, 5))
    # fig.add_subplot(1, 2, 1)
    # # print(m_array)
    # for j in range(0, 5):
    #     lab1.show_vector_points1(samples_array[j], colors_array[j])
    # for m in m_array:
    #     plt.scatter(m[0], m[1], marker='o', color='black', alpha=0.6, s=100)
    #
    # fig.add_subplot(1, 2, 2)
    # plt.title(f'minmax for 5 classes')
    # x = np.arange(0, len(m_array) + 1)
    # plt.plot(x, max_dist_array, label='max distance')
    # t_dist_array = [0, 0, t_dist_array[2][0], t_dist_array[3][0], t_dist_array[4][0], t_dist_array[5][0]]
    # plt.plot(x, t_dist_array, label='typical distance')
    # plt.xlabel('count centers')
    # plt.legend()
    # plt.show()
    #
    # samples_array = [samples1, samples2, samples3, samples4, samples5]
    # samples_array_result = concatenate_samples(samples_array)
    # rng = np.random.default_rng(2)
    # K = 3
    # indexes = rng.choice(range(samples_array_result.shape[1]), K, replace=False)
    # centers, classes, stats = k_means_method(samples_array_result, K, indexes)
    # fig = plt.figure(figsize=(15, 5))
    # fig.add_subplot(1, 2, 1)
    # plt.title(f'k means for {K} classes')
    # for k in range(len(classes)):
    #     plt.scatter(classes[k][:, 0], classes[k][:, 1], label=f"cl{k}")
    # for c in centers:
    #     plt.scatter(c[0], c[1], marker='o', color='black', alpha=0.6, s=100)
    # fig.add_subplot(1, 2, 2)
    # plt.title(f'k means for {K} classes')
    # x = np.arange(3, 3 + len(stats))
    # plt.plot(x, stats, label='dependence of the number of changes on the iteration number')
    # plt.xlabel('count iteration')
    # plt.ylabel('count changed vectors')
    # plt.legend()
    # plt.show()

    rng_array = [np.random.default_rng(42), np.random.default_rng(1)]
    for rng in rng_array:
        samples_array = [samples1, samples2, samples3, samples4, samples5]
        samples_array_result = concatenate_samples(samples_array)
        K = 5
        indexes = rng.choice(range(samples_array_result.shape[1]), K, replace=False)
        centers, classes, stats = k_means_method(samples_array_result, K, indexes)
        fig = plt.figure(figsize=(15, 5))
        fig.add_subplot(1, 2, 1)
        plt.title(f'k means for {K} classes')
        for k in range(len(classes)):
            plt.scatter(classes[k][:, 0], classes[k][:, 1], label=f"cl{k}")
        for c in centers:
            plt.scatter(c[0], c[1], marker='o', color='black', alpha=0.6, s=100)
        fig.add_subplot(1, 2, 2)
        plt.title(f'k means for {K} classes')
        x = np.arange(3, 3 + len(stats))
        plt.plot(x, stats, label='dependence of the number of changes on the iteration number')
        plt.xlabel('count iteration')
        plt.ylabel('count changed vectors')
        plt.legend()
        plt.show()
