import os
import numpy as np
import pandas as pd
from laspy.file import File
from sklearn.neighbors import NearestNeighbors
import warnings
import random

random.seed(0)
from random import random, shuffle


warnings.simplefilter(action="ignore")


def load_all_las_from_folder(args):
    las_folder = args.las_placettes_folder_path

    # We open las files and create a training dataset
    nparray_clouds_dict = {}  # dict to store numpy array with each plot separately
    xy_centers_dict = (
        {}
    )  # we keep track of plots means to reverse the normalisation in the future

    # We iterate through las files and transform them to np array
    las_files = os.listdir(las_folder)
    las_files = [l for l in las_files if l.lower().endswith(".las")]

    if args.mode == "DEV":
        shuffle(las_files)
        las_files = las_files[: (5 * 5)]  # nb plot by fold

        # #LOOK AT SPECIFIC FILES
        # las_files = las_files[:10] + [
        #     l
        #     for l in las_files
        #     if any(n in l for n in ["OBS15", "F68", "2021_POINT_OBS2"])
        # ]

        print(las_files)
    all_points_nparray = np.empty((0, args.nb_feats_for_train))
    for las_file in las_files:
        # Parse LAS files
        points_nparray, xy_centers = load_and_clean_single_las(las_folder, las_file)
        # HERE: extract KNN normalization
        points_nparray = transform_features_of_plot_cloud(
            points_nparray, args.znorm_radius_in_meters
        )
        all_points_nparray = np.append(all_points_nparray, points_nparray, axis=0)
        nparray_clouds_dict[os.path.splitext(las_file)[0]] = points_nparray
        xy_centers_dict[os.path.splitext(las_file)[0]] = xy_centers

    return all_points_nparray, nparray_clouds_dict, xy_centers_dict


# TODO: simplify the signature so that only one argument (las_filename) is needed.
def load_and_clean_single_las(las_folder, las_file):
    """Load a LAD file into a np.array, convert coordinates to meters, clean a few anomalies in plots."""
    # Parse LAS files
    las = File(os.path.join(las_folder, las_file), mode="r")
    x_las = las.X / 100  # we divide by 100 as all the values in las are in cm
    y_las = las.Y / 100
    z_las = las.Z / 100
    r = las.Red
    g = las.Green
    b = las.Blue
    nir = las.nir
    intensity = las.intensity
    return_nb = las.return_num
    points_nparray = np.asarray(
        [x_las, y_las, z_las, r, g, b, nir, intensity, return_nb]
    ).T

    # There is a file with 2 points 60m above others (maybe birds), we delete these points
    if las_file == "Releve_Lidar_F70.las":
        points_nparray = points_nparray[points_nparray[:, 2] < 640]
    # We do the same for the intensity
    if las_file == "POINT_OBS8.las":
        points_nparray = points_nparray[points_nparray[:, -2] < 32768]
    if las_file == "Releve_Lidar_F39.las":
        points_nparray = points_nparray[points_nparray[:, -2] < 20000]

    # get the average
    xy_centers = [
        (x_las.max() - x_las.min()) / 2.0,
        (y_las.max() - y_las.min()) / 2.0,
    ]
    return points_nparray, xy_centers


def transform_features_of_plot_cloud(points_nparray, znorm_radius_in_meters):
    """From the loaded points_nparray, process features and add additional ones.
    This is different from [0;1] normalization which is performed in
    1) Add a feature:min-normalized using min-z of the plot
    2) Substract z_min at local level using KNN
    """

    zmin_plot = np.min(points_nparray[:, 2])
    points_nparray = np.append(
        points_nparray, points_nparray[:, 2:3] - zmin_plot, axis=1
    )

    points_nparray = normalize_z_with_minz_in_a_radius(
        points_nparray, znorm_radius_in_meters
    )
    return points_nparray


def normalize_z_with_minz_in_a_radius(points_placette, znorm_radius_in_meters):
    # # We directly substract z_min at local level
    xyz = points_placette[:, :3]
    knn = NearestNeighbors(500, algorithm="kd_tree").fit(xyz[:, :2])
    _, neigh = knn.radius_neighbors(xyz[:, :2], znorm_radius_in_meters)
    z = xyz[:, 2]
    zmin_neigh = []
    for n in range(
        len(z)
    ):  # challenging to make it work without a loop as neigh has different length for each point
        zmin_neigh.append(np.min(z[neigh[n]]))
    points_placette[:, 2] = points_placette[:, 2] - zmin_neigh
    return points_placette


def normalize_z_with_approximate_DTM(points_placette, args):
    pass


def open_metadata_dataframe(args, pl_id_to_keep):
    """This opens the ground truth file. It completes if necessary admissibility value using ASP method.
    Values are kept as % as they are transformed during data loading into ratios."""

    df_gt = pd.read_csv(
        args.gt_file_path,
        sep=",",
        header=0,
    )  # we open GT file
    # Here, adapt columns names
    df_gt = df_gt.rename(args.coln_mapper_dict, axis=1)

    # Keep metadata for placettes we are considering
    df_gt = df_gt[df_gt["Name"].isin(pl_id_to_keep)]

    # Correct Soil value to have
    df_gt["COUV_SOL"] = 100 - df_gt["COUV_BASSE"]

    # his is ADM based on ASP definition - NOT USED at the moment
    if "ADM" not in df_gt:
        df_gt["ADM_BASSE"] = df_gt["COUV_BASSE"] - df_gt["NON_ACC_1"]
        df_gt["ADM_INTER"] = df_gt["COUV_HAUTE"] - df_gt["NON_ACC_2"]
        df_gt["ADM"] = df_gt[["ADM_BASSE", "ADM_INTER"]].max(axis=1)

        del df_gt["ADM_BASSE"]
        del df_gt["ADM_INTER"]

    # check that we have all columns we need
    assert all(
        coln in df_gt
        for coln in [
            "Name",
            "COUV_BASSE",
            "COUV_SOL",
            "COUV_INTER",
            "COUV_HAUTE",
            "ADM",
        ]
    )

    placettes_names = df_gt[
        "Name"
    ].to_numpy()  # We extract the names of the plots to create train and test list

    return df_gt, placettes_names
