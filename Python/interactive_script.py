import SimpleITK as sitk
import os
import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, fixed
import gui

# If the environment variable SIMPLE_ITK_MEMORY_CONSTRAINED_ENVIRONMENT is set, this will override the ReadImage
# function so that it also resamples the image to a smaller size (testing environment is memory constrained).
exec(open('setup_for_testing.py').read())

exec(open('update_path_to_download_script.py').read())
from downloaddata import fetch_data as fdata

# This is the registration configuration which we use in all cases. The only parameter that we vary
# is the initial_transform.
def multires_registration(fixed_image, moving_image, initial_transform):
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.01)
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsGradientDescent(
        learningRate=1.0,
        numberOfIterations=100,
        estimateLearningRate=registration_method.Once,
    )
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    registration_method.SetShrinkFactorsPerLevel(shrinkFactors=[4, 2, 1])
    registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2, 1, 0])
    registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

    final_transform = registration_method.Execute(fixed_image, moving_image)
    print(f"Final metric value: {registration_method.GetMetricValue()}")
    print(
        f"Optimizer's stopping condition, {registration_method.GetOptimizerStopConditionDescription()}"
    )
    return (final_transform, registration_method.GetMetricValue())

data_directory = os.path.dirname(fdata("CIRS057A_MR_CT_DICOM/readme.txt"))

fixed_series_ID = "1.2.840.113619.2.290.3.3233817346.783.1399004564.515"
moving_series_ID = "1.3.12.2.1107.5.2.18.41548.30000014030519285935000000933"

reader = sitk.ImageSeriesReader()
fixed_image = sitk.ReadImage(
    reader.GetGDCMSeriesFileNames(data_directory, fixed_series_ID), sitk.sitkFloat32
)
moving_image = sitk.ReadImage(
    reader.GetGDCMSeriesFileNames(data_directory, moving_series_ID), sitk.sitkFloat32
)

# To provide a reasonable display we need to window/level the images. By default we could have used the intensity
# ranges found in the images [SimpleITK's StatisticsImageFilter], but these are not the best values for viewing.
# Try using the full intensity range in the GUI to see that it is not a good choice for visualization.
ct_window_level = [932, 180]
mr_window_level = [286, 143]

gui.MultiImageDisplay(
    image_list=[fixed_image, moving_image],
    title_list=["fixed image", "moving image"],
    figure_size=(8, 4),
    window_level_list=[ct_window_level, mr_window_level],
    intensity_slider_range_percentile=[0, 100],
)

plt.show()