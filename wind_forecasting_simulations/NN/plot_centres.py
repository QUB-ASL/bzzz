# import matplotlib.pyplot as plt
# import numpy as np

# # Provided data
# data = np.array([
#  [2, 2, 2, 2, 2],
#  [5, 5, 5, 5, 5],
#  [8, 8, 8, 8, 8],
#  [1, 3, 5, 7, 9],
#  [9, 7, 5, 3, 1],
#  [4, 6, 4, 6, 4]
# ])

# some = [0.3, 0.3, 0.3, 0.3, 0.3, 1]  # Adjust alpha for transparency
# x = 0

# # Plotting
# plt.figure(figsize=(10, 6))
# for row in data:
#     plt.plot(range(1, 6), row, marker='o', linewidth=4, markersize=10, alpha=some[x])
#     x += 1
# plt.xlabel('Time Steps', fontsize=20)
# plt.ylabel('Wind Velocity (m/s)', fontsize=20)
# plt.title('Centre shapes', fontsize=26)
# plt.xticks(range(1, 6), ['t-4', 't-3', 't-2', 't-1', 't'], fontsize=18)
# plt.yticks(fontsize=18)
# plt.ylim(0.5, 9.5)
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# # plt save
# plt.savefig('wind_shapes_3.png')



import matplotlib.pyplot as plt
import numpy as np
# Background data
data = np.array([
    [2, 2, 2, 2, 2],
    [5, 5, 5, 5, 5],
    [8, 8, 8, 8, 8],
    [1, 3, 5, 7, 9],
    [9, 7, 5, 3, 1],
    [4, 6, 4, 6, 4]
])

# X-axis values
x_vals = range(1, 6)

# Number of random lines to generate
n_random_lines = 50

# Plot frames
for i in range(n_random_lines):
    plt.figure(figsize=(10, 6))

    # Plot background lines
    for row in data:
        plt.plot(x_vals, row, marker='o', linewidth=4, markersize=10, alpha=0.3)

    # Generate one random line (same length as a row in data)
    random_line = np.random.uniform(low=1, high=9, size=5)
    plt.plot(x_vals, random_line, marker='o', linewidth=4, markersize=10, alpha=1.0, color='blue')

    # Labels and styling
    plt.xlabel('Time Steps', fontsize=20)
    plt.ylabel('Wind Velocity (m/s)', fontsize=20)
    plt.title('Centre shapes', fontsize=26)
    plt.xticks(x_vals, ['t-4', 't-3', 't-2', 't-1', 't'], fontsize=18)
    plt.yticks(fontsize=18)
    plt.ylim(0.5, 9.5)
    plt.grid(True)
    plt.tight_layout()

    # Save frame
    plt.savefig(f'centre_frames/frame_{i:02d}.png')
    plt.close()
    # plt.show()













# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.stats import skewnorm

# # X values for the skew-normal distribution
# x_vals = np.linspace(-4, 4, 100)

# # Skewness levels to visualize
# skew_levels = np.linspace(-10, 10, 21)  # Negative to positive skew
# skew_levels = np.append(skew_levels, np.linspace(10, -10, 21))

# # Background data (symmetric for visual reference)
# data = [
#     skewnorm.pdf(x_vals, a=0),  # Normal distribution
# ]

# # Plot frames for each skew level
# for i, skew_param in enumerate(skew_levels):
#     plt.figure(figsize=(10, 6))

#     # Plot background (normal bell shape)
#     for row in data:
#         plt.plot(x_vals, row, linewidth=4, alpha=0.3, color='gray')

#     # Generate skewed shape and plot it
#     y_vals = skewnorm.pdf(x_vals, a=skew_param)
#     plt.plot(x_vals, y_vals, marker='o', markersize=4, linewidth=3, color='blue', alpha=1.0)

#     # Labels and styling
#     plt.xlabel('Value', fontsize=20)
#     plt.ylabel('Density (Shape)', fontsize=20)
#     plt.ylim(0, 0.8)  # Adjust y-limits for better visibility
#     plt.title(f'Shape with Skewness Param: {skew_param:.2f}', fontsize=26)
#     plt.xticks(fontsize=16)
#     plt.yticks(fontsize=16)
#     plt.grid(True)
#     plt.tight_layout()

#     # Save frame
#     plt.savefig(f'skew_shape_frames/frame_{i:02d}.png')
#     plt.close()
#     # plt.show()  # Show the plot for visualization







# import matplotlib.pyplot as plt
# import numpy as np
# from scipy.stats import gennorm, kurtosis

# # X values
# x_vals = np.linspace(-4, 4, 100)

# # Beta values to control kurtosis (lower = higher kurtosis)
# # Beta < 2 => leptokurtic (heavy tails), Beta = 2 => normal, Beta > 2 => platykurtic (flat)
# beta_values = np.linspace(0.5, 5.0, 19)
# beta_values = np.append(beta_values, np.linspace(5.0, 0.5, 19))  # Add reverse for more frames

# # Background (normal distribution shape)
# background = gennorm.pdf(x_vals, beta=2)

# # Plot frames
# for i, beta in enumerate(beta_values):
#     plt.figure(figsize=(10, 6))

#     # Plot background normal shape
#     plt.plot(x_vals, background, linewidth=4, alpha=0.3, color='gray')

#     # Generate distribution with current beta
#     y_vals = gennorm.pdf(x_vals, beta)

#     # Plot shape
#     plt.plot(x_vals, y_vals, marker='o', markersize=4, linewidth=3, color='purple', alpha=1.0)

#     # Compute excess kurtosis for annotation
#     sample = gennorm.rvs(beta, size=10000)
#     excess_kurt = kurtosis(sample)  # Already excess kurtosis (Fisher’s definition)

#     # Labels and styling
#     plt.xlabel('Value', fontsize=20)
#     plt.ylabel('Density (Shape)', fontsize=20)
#     plt.ylim(0, 0.6)  # Adjust y-limits for better visibility
#     plt.title(f'Shape with Beta: {beta:.2f} (Excess Kurtosis: {excess_kurt:.2f})', fontsize=22)
#     plt.xticks(fontsize=16)
#     plt.yticks(fontsize=16)
#     plt.grid(True)
#     plt.tight_layout()

#     # Save frame
#     plt.savefig(f'kurtosis_shape_frames/frame_{i:02d}.png')
#     plt.close()
#     # plt.show()  # Show the plot for visualization

















####################################################################








# import numpy as np
# import matplotlib.pyplot as plt

# # Distance values (||x - c||)
# r = np.linspace(0, 5, 400)

# # Gaussian RBF kernel
# def gaussian_rbf(r, gamma):
#     return np.exp(-r**2 / (2 * gamma**2))

# # Values of gamma to show
# gammas = [0.2, 0.5, 1.0, 2.0]

# # Plot
# plt.figure(figsize=(10, 6))
# for gamma in gammas:
#     plt.plot(r, gaussian_rbf(r, gamma), label=f"$\\gamma = {gamma}$", linewidth=4)

# plt.title("Gaussian RBF Kernel", fontsize=26)
# plt.xlabel(r"$\|x - c\|$", fontsize=20)
# plt.xticks(fontsize=18)
# plt.ylabel(r"$\exp\left(-\frac{\|x - c\|^2}{2\gamma^2}\right)$", fontsize=20)
# plt.yticks(fontsize=18)
# plt.legend(fontsize=18)
# plt.grid(True)
# plt.tight_layout()
# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt

# # Define a range of distances (||x - c||)
# r = np.linspace(0, 5, 400)

# # Define kernel functions
# def gaussian(r, gamma):
#     return np.exp(-r**2 / (2 * gamma**2))

# def multiquadric(r, gamma):
#     return np.sqrt(r**2 + gamma**2)

# def inverse_multiquadric(r, gamma):
#     return 1 / np.sqrt(r**2 + gamma**2)

# def thin_plate_spline(r, gamma):
#     with np.errstate(divide='ignore', invalid='ignore'):
#         # Avoid log(0) errors
#         tps = r**2 * np.log(r / gamma)
#         tps[r == 0] = 0
#         return tps

# # List of gamma values to visualize
# gammas = [0.2, 0.5, 1.0, 2.0]

# # Plot all kernels
# kernels = {
#     'Gaussian': gaussian,
#     'Multiquadric': multiquadric,
#     'Inverse Multiquadric': inverse_multiquadric,
#     'Thin Plate Spline': thin_plate_spline
# }

# fig, axs = plt.subplots(2, 2, figsize=(12, 8))
# axs = axs.ravel()

# for i, (name, kernel_fn) in enumerate(kernels.items()):
#     for gamma in gammas:
#         y = kernel_fn(r, gamma)
#         axs[i].plot(r, y, label=f'γ = {gamma}')
#     axs[i].set_title(name)
#     axs[i].set_xlabel(r"$\|x - c\|$")
#     axs[i].set_ylabel(r"$\rho(\|x - c\|)$")
#     axs[i].legend()
#     axs[i].grid(True)

# plt.tight_layout()
# plt.show()


















# import numpy as np
# import matplotlib.pyplot as plt

# # 1D input space for visualization
# x = np.linspace(-5, 10, 500)

# # Distance metric between two centers
# def rbf(x, c, gamma):
#     return np.exp(-((x - c) ** 2) / (2 * gamma ** 2))

# # Parameters
# alphas = [0.2, 0.5, 1.0, 2.0]  # α values to scale γ
# c1, c2 = 0.0, 2.0              # centers (distance d = 2.0)
# d = np.abs(c2 - c1)           # distance between centers

# # Plotting
# plt.figure(figsize=(10, 6))
# for alpha in alphas:
#     gamma = alpha * d
#     y1 = rbf(x, c1, gamma)
#     y2 = rbf(x, c2, gamma)
#     plt.plot(x, y1, label=f'Center at {c1}, α={alpha}', linestyle='--')
#     plt.plot(x, y2, label=f'Center at {c2}, α={alpha}')

# plt.title("Overlap of Two Gaussian RBFs with Distance-Dependent γ", fontsize=20)
# plt.xlabel("x", fontsize=16)
# plt.ylabel("RBF Value", fontsize=16)
# plt.legend(fontsize=12)
# plt.grid(True)
# plt.tight_layout()
# plt.show()



# import numpy as np
# import matplotlib.pyplot as plt
# import os

# # RBF function
# def gaussian_rbf(x, center, gamma):
#     return np.exp(-((x - center) ** 2) / (2 * gamma ** 2))

# # Input space
# x = np.linspace(-15, 15, 500)

# # Centers of the two RBFs
# c1, c2 = -2.5, 2.5
# d = np.abs(c2 - c1)

# # Alpha values for animation (forward and reverse)
# alpha_values = [0.1, 0.1, 0.1, 0.2, 0.4, 0.5, 0.8, 1.0, 2.0 ]
# alpha_values = np.concatenate([alpha_values, alpha_values[::-1]])  # loop back

# # Background RBF shape (midpoint alpha)
# gamma_bg = 1.0 * d
# background_rbf_1 = gaussian_rbf(x, c1, gamma_bg)
# background_rbf_2 = gaussian_rbf(x, c2, gamma_bg)

# # Generate frames
# for i, alpha in enumerate(alpha_values):
#     gamma = alpha * d
#     y1 = gaussian_rbf(x, c1, gamma)
#     y2 = gaussian_rbf(x, c2, gamma)

#     # Combined RBF shape
#     combined = y1 + y2

#     plt.figure(figsize=(10, 6))

#     # Plot background shape
#     # plt.plot(x, background_rbf_1, linewidth=4, alpha=0.3, color='gray', label='Reference (α=1.0)')
#     # plt.plot(x, background_rbf_2, linewidth=4, alpha=0.3, color='gray')

#     # Plot current RBFs
#     plt.plot(x, y1, color='blue', linewidth=4)
#     plt.plot(x, y2, color='red', linewidth=4)
#     # plt.plot(x, combined, color='purple', linestyle='--', linewidth=3, label='Sum')

#     # Styling
#     plt.xlabel("x", fontsize=20)
#     plt.ylabel("RBF Value", fontsize=20)
#     plt.ylim(0, 1)
#     plt.title(f"RBF Overlap - $\\alpha = ${alpha:.2f}, $\\gamma = \\alpha \cdot d = ${gamma:.2f}", fontsize=26)
#     plt.xticks(fontsize=18)
#     plt.yticks(fontsize=18)
#     plt.grid(True)
#     # plt.legend(fontsize=14)
#     plt.tight_layout()

#     # Save frame
#     # plt.savefig(f"gamma_frames/frame_{i:02d}.png")
#     # plt.close()
#     plt.show()  # Show the plot for visualization
