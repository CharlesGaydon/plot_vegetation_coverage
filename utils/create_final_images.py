import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.gridspec as gridspec

import numpy as np
import torch
from osgeo import gdal, osr
from utils.useful_functions import print_stats
import torch.nn as nn

plt.rcParams["font.size"] = 25


def visualize_article(
    image_soil, image_med_veg, image_high_veg, cloud, pl_id, stats_path, args, txt=None
):

    fig = plt.figure(figsize=(15, 12))
    gs = gridspec.GridSpec(3, 3)

    # Original point data
    ax1 = fig.add_subplot(gs[:, 0:2], projection="3d")
    colors_ = cloud[3:6].numpy().transpose()
    ax1.scatter(
        cloud[0],
        cloud[1],
        cloud[2] * args.z_max,
        c=colors_,
        vmin=0,
        vmax=1,
        s=10,
        alpha=1,
    )
    ax1.auto_scale_xyz
    ax1.set_yticklabels([])
    ax1.set_xticklabels([])
    # colors = cloud[3:7].numpy().transpose()
    # ax1.scatter3D(cloud[0], cloud[1], cloud[2], c=cloud[[6, 3, 4]].numpy().transpose(), s=2, vmin=0, vmax=10)
    ax1.set_title(pl_id)
    for line in ax1.xaxis.get_ticklines():
        line.set_visible(False)
    for line in ax1.yaxis.get_ticklines():
        line.set_visible(False)

    # LV stratum raster
    ax2 = fig.add_subplot(gs[0, 2])
    color_grad = [(0.8, 0.4, 0.1), (0, 1, 0)]  # first color is white, last is green
    cm = colors.LinearSegmentedColormap.from_list("Custom", color_grad, N=100)
    ax2.imshow(image_soil, cmap=cm, vmin=0, vmax=1)
    ax2.set_title("Ground level")
    ax2.tick_params(
        axis="both",  # changes apply to both axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
    )  # labels along the bottom edge are off
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])

    # MV stratum raster
    ax3 = fig.add_subplot(gs[1, 2])
    color_grad = [(1, 1, 1), (0, 1, 0)]  # first color is white, last is green
    cm = colors.LinearSegmentedColormap.from_list("Custom", color_grad, N=100)
    ax3.imshow(image_med_veg, cmap=cm, vmin=0, vmax=1)
    ax3.set_title("Medium level")
    ax3.tick_params(
        axis="both",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
    )  # labels along the bottom edge are off
    ax3.set_yticklabels([])
    ax3.set_xticklabels([])

    # Plot high vegetation stratum
    ax4 = fig.add_subplot(gs[2, 2])
    color_grad = [(1, 1, 1), (0, 1, 0)]  # first color is white, last is red
    cm = colors.LinearSegmentedColormap.from_list("Custom", color_grad, N=100)
    ax4.imshow(image_high_veg, cmap=cm, vmin=0, vmax=1)
    ax4.set_title("High level")
    ax4.tick_params(
        axis="both",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
    )  # labels along the bottom edge are off
    ax4.set_yticklabels([])
    ax4.set_xticklabels([])

    if txt is not None:
        fig.text(0.5, 0.05, txt, ha="center")
    plt.savefig(
        stats_path + pl_id + "_article.svg", format="svg", bbox_inches="tight", dpi=300
    )
    plt.clf()
    plt.close("all")


def visualize(
    image_low_veg,
    image_med_veg,
    cloud,
    prediction,
    pl_id,
    stats_path,
    args,
    text_pred_vs_gt=None,
    scores=None,
    image_high_veg=None,
    predictions=["Vb", "soil", "Vm", "Vh", "Adm"],
    gt=["Vb", "soil", "Vm", "Vh", "Adm"],
):

    if image_low_veg.ndim == 3:
        image_low_veg = image_low_veg[:, :, 0]
        image_med_veg = image_med_veg[:, :, 0]

    # We set figure size depending on the number of subplots
    if scores is None and image_high_veg is None:
        row, col = 2, 2
        fig = plt.figure(figsize=(20, 15))
    else:
        row, col = 3, 2
        fig = plt.figure(figsize=(20, 25))

    # Original point data
    ax1 = fig.add_subplot(row, col, 1, projection="3d")
    colors_ = cloud[3:6].numpy().transpose()
    ax1.scatter(
        cloud[0],
        cloud[1],
        cloud[2] * args.z_max,
        c=colors_,
        vmin=0,
        vmax=1,
        s=10,
        alpha=1,
    )
    ax1.auto_scale_xyz
    ax1.set_yticklabels([])
    ax1.set_xticklabels([])
    # colors = cloud[3:7].numpy().transpose()
    # ax1.scatter3D(cloud[0], cloud[1], cloud[2], c=cloud[[6, 3, 4]].numpy().transpose(), s=2, vmin=0, vmax=10)
    ax1.set_title(pl_id)

    # LV stratum raster
    ax2 = fig.add_subplot(row, col, 2)
    color_grad = [
        (0.8, 0.4, 0.1),
        (0.91, 0.91, 0.91),
        (0, 1, 0),
    ]  # first color is brown, second is grey, last is green
    cm = colors.LinearSegmentedColormap.from_list("Custom", color_grad, N=100)
    ax2.imshow(image_low_veg, cmap=cm, vmin=0, vmax=1)
    ax2.set_title(f"Low veg. = {predictions[0]:.0%} (gt={gt[0]:.0%})")
    ax2.tick_params(
        axis="both",  # changes apply to both axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
    )  # labels along the bottom edge are off
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    PCM = ax2.get_children()[9]
    plt.colorbar(PCM, ax=ax2)

    # Pointwise prediction
    ax3 = fig.add_subplot(row, col, 3, projection="3d")
    ax3.auto_scale_xyz
    colors_pred = prediction.cpu().detach().numpy().transpose()
    color_matrix = [[0, 1, 0], [0.8, 0.4, 0.1], [0, 0, 1], [1, 0, 0]]
    colors_pred = np.matmul(colors_pred, color_matrix)
    ax3.scatter(
        cloud[0],
        cloud[1],
        cloud[2] * args.z_max,
        c=colors_pred,
        s=10,
        vmin=0,
        vmax=1,
        alpha=1,
    )
    ax3.set_title("Pointwise prediction")
    ax3.set_yticklabels([])
    ax3.set_xticklabels([])

    # MV stratum raster
    ax4 = fig.add_subplot(row, col, 4)
    color_grad = [(1, 1, 1), (0, 0, 1)]  # first color is white, last is blue
    cm = colors.LinearSegmentedColormap.from_list("Custom", color_grad, N=100)
    ax4.imshow(image_med_veg, cmap=cm, vmin=0, vmax=1)
    ax4.set_title(f"Medium veg. = {predictions[2]:.0%} (gt={gt[2]:.0%})")
    ax4.tick_params(
        axis="both",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        left=False,
        right=False,
        labelbottom=False,
    )  # labels along the bottom edge are off
    ax4.set_yticklabels([])
    ax4.set_xticklabels([])
    PCM = ax4.get_children()[9]
    plt.colorbar(PCM, ax=ax4)

    # Plot stratum scores
    if scores is not None:
        ax5 = fig.add_subplot(row, col, 5, projection="3d")
        ax5.auto_scale_xyz
        sc_sum = scores.sum(1)
        scores[:, 0] = scores[:, 0] / sc_sum
        scores[:, 1] = scores[:, 1] / sc_sum
        scores = scores / (scores.max())
        colors_pred = (
            scores.transpose(1, 0)[[0, 0, 1], :].cpu().detach().numpy().transpose()
        )
        ax5.scatter(
            cloud[0],
            cloud[1],
            cloud[2] * args.z_max,
            c=colors_pred,
            s=10,
            vmin=0,
            vmax=1,
        )
        ax5.set_title("Ground vs. non-ground")
        ax5.set_yticklabels([])
        ax5.set_xticklabels([])

    # Plot high vegetation stratum
    if image_high_veg is not None:
        ax6 = fig.add_subplot(row, col, 6)
        color_grad = [(1, 1, 1), (1, 0, 0)]  # first color is white, last is red
        cm = colors.LinearSegmentedColormap.from_list("Custom", color_grad, N=100)
        ax6.imshow(image_high_veg, cmap=cm, vmin=0, vmax=1)
        ax6.set_title(f"High veg. = {predictions[3]:.0%} (gt={gt[3]:.0%})")
        ax6.tick_params(
            axis="both",  # changes apply to the x-axis
            which="both",  # both major and minor ticks are affected
            bottom=False,  # ticks along the bottom edge are off
            top=False,  # ticks along the top edge are off
            left=False,
            right=False,
            labelbottom=False,
        )  # labels along the bottom edge are off
        ax6.set_yticklabels([])
        ax6.set_xticklabels([])
        PCM = ax6.get_children()[9]
        plt.colorbar(PCM, ax=ax6)

    if text_pred_vs_gt is not None:
        fig.text(0.5, 0.05, text_pred_vs_gt, ha="center")
    plt.savefig(stats_path + pl_id + ".png", format="png", bbox_inches="tight", dpi=300)
    plt.clf()
    plt.close("all")


def create_final_images(
    pred_pl,
    gt,
    pred_pointwise_b,
    cloud,
    likelihood,
    plot_name,
    mean_dataset,
    stats_path,
    stats_file,
    args,
    create_and_save_raster_as_TIFF_file=True,
    adm=None,
):
    """
    We do final data reprojection to the 2D space (2 stratum - ground vegetation level and medium level, optionally high level)
    by associating the points to the pixels.
    Then we create the images with those stratum
    """
    for b in range(len(pred_pointwise_b)):
        # we get prediction stats string
        pred_pointwise = pred_pointwise_b[b]
        current_cloud = cloud[b]  # (9, N) tensor
        plot_center = mean_dataset[plot_name]  # tuple (x,y)

        # we do raster reprojection, but we do not use torch scatter as we have to associate each value to a pixel
        image_low_veg, image_med_veg, image_high_veg = infer_and_project_on_rasters(
            current_cloud, args, pred_pointwise
        )
        # We normalize back x,y values to create a tiff file with 2 rasters
        if create_and_save_raster_as_TIFF_file:
            xy = (
                current_cloud[:2, :].detach().cpu().numpy()
            )  # (2, N) tensor -> (2, N) nparray
            img_to_write, geo = rescale_xy_and_get_geotransformation_(
                xy,
                plot_center,
                args,
                image_low_veg,
                image_med_veg,
                image_high_veg,
            )
            create_tiff(
                nb_channels=args.nb_stratum,
                new_tiff_name=stats_path + plot_name + ".tif",
                width=args.diam_pix,
                height=args.diam_pix,
                datatype=gdal.GDT_Float32,
                data_array=img_to_write,
                geotransformation=geo,
            )

        if args.adm:
            preds_nparray = np.round(
                np.asarray(pred_pl[b].cpu().detach().numpy().reshape(-1)), 2
            )
            adm_ = adm[b].cpu().detach().numpy().round(2)
            gt_nparray = gt.cpu().numpy()[0]
            text_pred_vs_gt = (
                f"Coverage: Pred {preds_nparray[:4]} GT   {gt_nparray[:-1]}\n "
                + f"Admissibility: Pred {adm_:.2f}  GT  {gt_nparray[-1]:.2f}"
            )
        else:
            preds_nparray = np.round(
                np.asarray(pred_pl[b].cpu().detach().numpy().reshape(-1)), 2
            )
            gt_nparray = gt.cpu().numpy()[0]
            text_pred_vs_gt = (
                f"Coverage: Pred {preds_nparray[:4]} GT   {gt_nparray[:-1]}\n "
                + f"Admissibility (GT only) {gt_nparray[-1]:.2f}"
            )

        text_pred_vs_gt = "LOW, soil, MID, HIGH \n" + text_pred_vs_gt
        print_stats(
            stats_file, plot_name + " " + text_pred_vs_gt, print_to_console=True
        )
        # We create an image with 5 or 6 subplots:
        # 1. original point cloud, 2. LV image, 3. pointwise prediction point cloud, 4. MV image, 5.Stratum probabilities point cloud, 6.(optional) HV image
        visualize(
            image_low_veg,
            image_med_veg,
            current_cloud,
            pred_pointwise,
            plot_name,
            stats_path,
            args,
            text_pred_vs_gt=text_pred_vs_gt,
            scores=likelihood,
            image_high_veg=image_high_veg,
            predictions=preds_nparray,
            gt=gt_nparray,
        )
        if args.nb_stratum == 3:
            visualize_article(
                image_low_veg,
                image_med_veg,
                image_high_veg,
                current_cloud,
                plot_name,
                stats_path,
                args,
                txt=text_pred_vs_gt,
            )


def rescale_xy_and_get_geotransformation_(
    xy, plot_center_xy, args, image_low_veg, image_med_veg, image_high_veg
):
    xy = xy * 10 + np.asarray(plot_center_xy).reshape(-1, 1)
    geo = [
        np.min(xy, axis=1)[0],
        (np.max(xy, axis=1)[0] - np.min(xy, axis=1)[0]) / args.diam_pix,
        0,
        np.max(xy, axis=1)[1],
        0,
        (-np.max(xy, axis=1)[1] + np.min(xy, axis=1)[1]) / args.diam_pix,
    ]
    if args.nb_stratum == 2:
        img_to_write = np.concatenate(([image_low_veg], [image_med_veg]), 0)
    else:
        img_to_write = np.concatenate(
            ([image_low_veg], [image_med_veg], [image_high_veg]), 0
        )
    return img_to_write, geo


def infer_and_project_on_rasters(current_cloud, args, pred_cloud):
    # we do raster reprojection, but we do not use torch scatter as we have to associate each value to a pixel
    # Outputs are
    """
    current_cloud: (2, N) 2D tensor
     image_low_veg, image_med_veg, image_high_veg
    """
    xy = current_cloud[:2, :]
    # center and normalize between 0 and 1 using MIN and MAX of points (instead of plot center  and width/height !)
    xy = torch.floor(
        (xy - torch.min(xy, dim=1).values.view(2, 1).expand_as(xy))
        / (torch.max(xy, dim=1).values - torch.min(xy, dim=1).values + 0.0001)
        .view(2, 1)
        .expand_as(xy)
        * args.diam_pix
    ).int()
    xy = xy.cpu().numpy()
    unique, index, inverse = np.unique(
        xy.T, axis=0, return_index=True, return_inverse=True
    )

    # we get the values for each unique pixel and write them to rasters
    image_low_veg = np.full((args.diam_pix, args.diam_pix), np.nan)
    image_med_veg = np.full((args.diam_pix, args.diam_pix), np.nan)
    if args.nb_stratum == 3:
        image_high_veg = np.full((args.diam_pix, args.diam_pix), np.nan)
    else:
        image_high_veg = None
    for i in np.unique(inverse):
        where = np.where(inverse == i)[0]
        k, m = xy.T[where][0]
        maxpool = nn.MaxPool1d(len(where))
        max_pool_val = (
            maxpool(pred_cloud[:, where].unsqueeze(0)).cpu().detach().numpy().flatten()
        )

        if args.norm_ground:  # we normalize ground level coverage values
            proba_low_veg = max_pool_val[0] / (max_pool_val[:2].sum())
        else:  # we do not normalize anything, as bare soil coverage does not participate in absolute loss
            proba_low_veg = max_pool_val[0]
        proba_med_veg = max_pool_val[2]
        image_low_veg[m, k] = proba_low_veg
        image_med_veg[m, k] = proba_med_veg

        if args.nb_stratum == 3:
            proba_high_veg = max_pool_val[3]
            image_high_veg[m, k] = proba_high_veg
    # we flip along y axis as the 1st raster row starts with 0
    image_low_veg = np.flip(image_low_veg, axis=0)
    image_med_veg = np.flip(image_med_veg, axis=0)
    if args.nb_stratum == 3:
        image_high_veg = np.flip(image_high_veg, axis=0)
    return image_low_veg, image_med_veg, image_high_veg


# We create a tiff file with 2 or 3 stratum
def create_tiff(
    nb_channels, new_tiff_name, width, height, datatype, data_array, geotransformation
):
    # We set Lambert 93 projection
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(2154)
    proj = srs.ExportToWkt()
    # We create a datasource
    driver_tiff = gdal.GetDriverByName("GTiff")
    dst_ds = driver_tiff.Create(new_tiff_name, width, height, nb_channels, datatype)
    if nb_channels == 1:
        dst_ds.GetRasterBand(1).WriteArray(data_array)
    else:
        for ch in range(nb_channels):
            dst_ds.GetRasterBand(ch + 1).WriteArray(data_array[ch])
    dst_ds.SetGeoTransform(geotransformation)
    dst_ds.SetProjection(proj)
    return dst_ds
