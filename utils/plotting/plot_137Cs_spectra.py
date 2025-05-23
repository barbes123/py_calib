import matplotlib.pyplot as plt
import numpy as np

# Define file paths
files = [
    "s1/addback_run_167_999_eliadeS1/sum_fold_1_4.spe",
    "s2/addback_run_164_999_eliadeS2/sum_fold_1_4.spe",
    "s3/addback_run_33_999_eliadeS3/sum_fold_1_4.spe"
]

# Function to read one-column .spe files
def read_spe(file_path):
    # Read the file assuming it has one column (representing either energy or intensity)
    data = np.loadtxt(file_path)
    return data  # Return the data directly (as the single column)

# Plot data from all files
plt.figure(figsize=(10, 6))

for file in files:
    data = read_spe(file)
    # Assuming energy starts from 0, incrementing by 1 for simplicity
    energy = np.arange(len(data))  # Generate dummy energy values (index of data)
    plt.plot(energy, data, label=f"Data from {file}")

# Customize the plot
plt.title(r"$^{137}Cs$ spectra")
plt.xlabel("Energy (keV)")  # Assuming energy values are in the x-axis
plt.ylabel("Counts (1 keV / bin))")
plt.xlim(0,2000)
plt.legend()
plt.grid(True)
plt.yscale('log')

plt.savefig('137Cs_fold_all.jpg', dpi = 300)

# Show the plot
plt.show()
