import json
import matplotlib.pyplot as plt
import numpy as np

import math

class GammaPeak:
    def __init__(self, energy, area, res, pos_ch):
        self.energy = energy
        self.area = area
        self.resolution = res
        self.pos_ch = pos_ch
        self.probability = None
        self.probability_error = None
        self.efficiency = None
        self.efficiency_uncertainty = None
        # New parameters for advanced efficiency calculation
        self.A0 = None
        self.sigma_A0 = None
        self.lambd = None
        self.sigma_lambd = None
        self.T1 = None
        self.sigma_T1 = None
        self.T2 = None
        self.sigma_T2 = None

    def calculate_efficiency(self, n_decays_sum, n_decays_sum_error=None):
        """Calculate efficiency and its error for this peak using the simple method"""
        if self.probability is not None and self.area is not None:
            expected_counts = self.probability * n_decays_sum
            # Efficiency Calculation
            self.efficiency = (self.area[0] / expected_counts) * 100.0

            # Efficiency Error Calculation
            area_uncertainty = self.area[1]
            probability_error = self.calculate_probability_error()

            efficiency_error = self.efficiency * ((area_uncertainty / self.area[0])**2 +
                                                (probability_error / self.probability)**2 +
                                                (n_decays_sum_error / n_decays_sum)**2)**0.5

            self.efficiency_uncertainty = efficiency_error * 100.0
            return self.efficiency, self.efficiency_uncertainty
        return None, None
    
    def calculate_advanced_efficiency(self, A0, sigma_A0, lambd, sigma_lambd, 
                                     T1, sigma_T1, T2, sigma_T2):
        """
        Calculate efficiency using the advanced method with full error propagation.
        
        Parameters:
        - A0: Initial activity in Bq at time t=0
        - sigma_A0: Uncertainty in A0
        - lambd: Decay constant in s^-1
        - sigma_lambd: Uncertainty in decay constant
        - T1: Start time in seconds relative to t=0
        - sigma_T1: Uncertainty in T1
        - T2: End time in seconds relative to t=0
        - sigma_T2: Uncertainty in T2
        
        The formula used is: 
        eta = Area / (N_expected * P)
        where:
        - N_expected = (A0/lambd) * (exp(-lambd*T1) - exp(-lambd*T2))
        - P is the probability of emission for this gamma energy
        """
        if self.area is None or self.area[0] is None:
            print(f"Warning: Area not available for energy {self.energy}")
            return None, None
            
        if self.probability is None:
            print(f"Warning: Probability not available for energy {self.energy}")
            return None, None
            
        # Store the parameters for future reference
        self.A0 = A0
        self.sigma_A0 = sigma_A0
        self.lambd = lambd
        self.sigma_lambd = sigma_lambd
        self.T1 = T1
        self.sigma_T1 = sigma_T1
        self.T2 = T2
        self.sigma_T2 = sigma_T2
        
        # Get area and its uncertainty
        Area = self.area[0]
        sigma_Area = self.area[1]
        
        # Get probability and its uncertainty
        P = self.probability
        sigma_P = self.probability_error if self.probability_error is not None else 0.0
        
        # Compute the exponential terms
        exp_T1 = math.exp(-lambd * T1)
        exp_T2 = math.exp(-lambd * T2)
        Q = exp_T1 - exp_T2
        
        # Check for potential numerical issues
        if abs(Q) < 1e-10:
            print(f"Warning: Very small time-dependent factor ({Q:.2e}) for energy {self.energy}. This may cause numerical instability.")
            if Q == 0:
                print("Error: Division by zero would occur. Cannot calculate efficiency.")
                return None, None
        
        # Compute expected number of decays (using the analytically solved integral)
        N_decays = (A0 / lambd) * Q
        
        # Compute expected number of gamma rays at this energy
        expected_counts = N_decays * P
        
        # Compute eta (efficiency)
        eta = Area / expected_counts
        
        # Convert to percentage
        eta_percent = eta * 100.0
        
        # Partial derivatives for error propagation
        
        #d_eta_d_Area = eta/Area
        d_eta_d_Area = 1.0 / expected_counts
        
        d_eta_d_A0 = -eta / A0

        #d_eta_d_lambd = eta * (1.0 / lambd + (T1 * exp_T1 - T2 * exp_T2) / Q)
        d_eta_d_lambd = 0

        d_eta_d_P = -eta / P
        
        d_eta_d_T1 = eta * (lambd * exp_T1) / Q
        
        d_eta_d_T2 = -eta * (lambd * exp_T2) / Q

        # Combine uncertainties (assuming independent errors)
        sigma_eta_squared = ((d_eta_d_Area * sigma_Area)**2 +
                            (d_eta_d_A0 * sigma_A0)**2 +
                            (d_eta_d_P * sigma_P)**2 +
                            (d_eta_d_lambd * sigma_lambd)**2 +
                            (d_eta_d_T1 * sigma_T1)**2 +
                            (d_eta_d_T2 * sigma_T2)**2)
        
        sigma_eta = math.sqrt(sigma_eta_squared)
        
        # Convert uncertainty to percentage
        sigma_eta_percent = sigma_eta * 100.0
        
        # Store the calculated values
        self.efficiency = eta_percent
        self.efficiency_uncertainty = sigma_eta_percent
        
        # Detailed logging for verification
        print(f"Advanced efficiency calculation for energy {self.energy} keV:")
        print(f"  - Area: {Area:.2f} ± {sigma_Area:.2f}")
        print(f"  - A0: {A0:.2e} ± {sigma_A0:.2e}")
        print(f"  - Decay constant (λ): {lambd:.2e} ± {sigma_lambd:.2e}")
        print(f"  - T1: {T1:.2f} ± {sigma_T1:.2f}")
        print(f"  - T2: {T2:.2f} ± {sigma_T2:.2f}")
        print(f"  - Probability: {P:.6f} ± {sigma_P:.6f}")
        print(f"  - Time factor (Q = exp(-λ*T1) - exp(-λ*T2)): {Q:.6e}")
        print(f"  - Total number of decays (N): {N_decays:.2e}")
        print(f"  - Expected counts at this energy: {expected_counts:.2f}")
        print(f"  - Efficiency: {eta_percent:.4f}% ± {sigma_eta_percent:.4f}%")
        print(f"  - Relative uncertainty: {(sigma_eta_percent/eta_percent)*100:.2f}%")
        
        # Add contribution breakdown for uncertainty analysis
        area_contrib = (d_eta_d_Area * sigma_Area)**2 / sigma_eta_squared * 100
        a0_contrib = (d_eta_d_A0 * sigma_A0)**2 / sigma_eta_squared * 100
        p_contrib = (d_eta_d_P * sigma_P)**2 / sigma_eta_squared * 100
        lambd_contrib = (d_eta_d_lambd * sigma_lambd)**2 / sigma_eta_squared * 100
        t1_contrib = (d_eta_d_T1 * sigma_T1)**2 / sigma_eta_squared * 100
        t2_contrib = (d_eta_d_T2 * sigma_T2)**2 / sigma_eta_squared * 100
        
        print("\nUncertainty contribution breakdown:")
        print(f"  - Area: {area_contrib:.1f}%")
        print(f"  - A0: {a0_contrib:.1f}%")
        print(f"  - Probability: {p_contrib:.1f}%")
        print(f"  - Decay constant: {lambd_contrib:.1f}%")
        print(f"  - T1: {t1_contrib:.1f}%")
        print(f"  - T2: {t2_contrib:.1f}%")
        
        return eta_percent, sigma_eta_percent

    def set_probability_error(self, probability_error):
        """Set the error for the probability"""
        self.probability_error = probability_error

    def calculate_probability_error(self):
        """Return the probability error or 0.0 if not set"""
        return self.probability_error if self.probability_error is not None else 0.0

    def set_area_error(self, area_error):
        """Set the error for the area"""
        self.area_error = area_error

class IsotopeData:
    def __init__(self, experimental_data, probabilities_data, source_name, n_decays_sum, n_decays_sum_error=None, tolerance=1):
        self.experimental_data = experimental_data
        self.probabilities_data = probabilities_data
        self.source_name = source_name
        self.domains_data = {}
        self.tolerance = tolerance
        self.n_decays_sum = n_decays_sum
        self.n_decays_sum_error = n_decays_sum_error
        self.efficiencies = []
        self.experimental_file_path = None
        # New parameters for advanced calculations
        self.A0 = None
        self.sigma_A0 = None
        self.lambd = None
        self.sigma_lambd = None
        self.T1 = None
        self.sigma_T1 = None
        self.T2 = None
        self.sigma_T2 = None
        
    def set_advanced_parameters(self, A0, sigma_A0, lambd, sigma_lambd, T1, sigma_T1, T2, sigma_T2):
        """Set parameters needed for advanced efficiency calculations"""
        self.A0 = A0
        self.sigma_A0 = sigma_A0
        self.lambd = lambd
        self.sigma_lambd = sigma_lambd
        self.T1 = T1
        self.sigma_T1 = sigma_T1
        self.T2 = T2
        self.sigma_T2 = sigma_T2
        
    def add_probabilities_to_peaks(self, use_advanced_calculation=False):
        """Update peaks with probabilities and calculate efficiencies
        
        Parameters:
        use_advanced_calculation: If True, use the advanced error propagation method
        """
        if self.source_name not in self.probabilities_data:
            print(f"Warning: Source {self.source_name} not found in probabilities data.")
            return

        source_probabilities = self.probabilities_data[self.source_name]
        gammas = source_probabilities.get("gammas", {})

        for gamma_energy_str, gamma_values in gammas.items():
            gamma_energy = float(gamma_energy_str)
            print(f"Extracted probability for Gamma Energy: {gamma_energy}, Values: {gamma_values}")

            for domain, domain_peaks in self.domains_data.items():
                matched_peak = None
                for energy, peak in domain_peaks.items():
                    if abs(energy - gamma_energy) <= self.tolerance:
                        matched_peak = peak
                        break

                if matched_peak:
                    resolution = gamma_values[0]
                    intensity = gamma_values[2]
                    prob = gamma_values[1]
                    # Make sure to extract the probability error correctly from your data structure
                    # Here I'm guessing it's at index 3, adjust as needed
                    prob_error = gamma_values[3] if len(gamma_values) > 3 else 0.0

                    matched_peak.resolution = resolution
                    matched_peak.pos_ch = intensity
                    matched_peak.probability = prob
                    matched_peak.set_probability_error(prob_error)  # Store probability error

                    print(f"Setting probability error for energy {gamma_energy}: {prob_error}")

                    if use_advanced_calculation and all(param is not None for param in 
                                                       [self.A0, self.sigma_A0, self.lambd, 
                                                        self.sigma_lambd, self.T1, self.sigma_T1, 
                                                        self.T2, self.sigma_T2]):
                        # Calculate efficiency using advanced method
                        matched_peak.calculate_advanced_efficiency(
                            self.A0, self.sigma_A0, self.lambd, self.sigma_lambd,
                            self.T1, self.sigma_T1, self.T2, self.sigma_T2
                        )
                    else:
                        # Use the simple method
                        matched_peak.calculate_efficiency(self.n_decays_sum, self.n_decays_sum_error)

                    # Update experimental data using the energy value
                    self.update_experimental_data(domain, matched_peak.energy,
                                                 matched_peak.efficiency,
                                                 matched_peak.efficiency_uncertainty)

                    print(f"Assigned resolution {resolution}, intensity {intensity}, probability {prob}, " 
                          f"and probability error {prob_error} to peak with energy {gamma_energy} in domain {domain}")
                else:
                    print(f"No match found for gamma energy {gamma_energy} in domain {domain} within tolerance of {self.tolerance}")
    
    def parse_experimental_data(self):
        """Parse experimental data and organize it"""
        print("Loaded experimental data:", self.experimental_data)

        for entry in self.experimental_data:
            isotope_data = entry.get(self.source_name)
            if isotope_data:
                print(f"Processing isotope data for domain {entry['domain']}...")
                self.domains_data[entry['domain']] = self._process_isotope_data(isotope_data)
            else:
                print(f"Warning: No isotope data found for {self.source_name} in domain {entry['domain']}")

    def print_probability_errors(self):
        """Print all probability errors for debugging and verification"""
        print("\nProbability Error Summary:")
        for domain, domain_peaks in self.domains_data.items():
            print(f"\nDomain: {domain}")
            for energy, peak in domain_peaks.items():
                if peak.probability is not None:
                    print(f"  Energy: {energy:.2f} keV, Probability: {peak.probability:.6f}" 
                          f" ± {peak.probability_error if peak.probability_error is not None else 'N/A'}")
    def _process_isotope_data(self, isotope_data):
        """Process isotope data into GammaPeak objects"""
        gamma_peaks = {}

        for energy_str, peak_data in isotope_data.items():
            try:
                energy_float = round(float(energy_str), 4)
            except ValueError:
                print(f"Skipping peak with invalid energy value: {energy_str}")
                continue

            print(f"Parsed Energy: {energy_float}, Peak Data: {peak_data}")

            area = [peak_data.get('area', [None])[0], peak_data.get('area', [None, None])[1]]  # Get both value and uncertainty
            res = peak_data.get('res', [None])[0]
            pos_ch = peak_data.get('pos_ch', None)

            gamma_peaks[energy_float] = GammaPeak(energy_float, area, res, pos_ch)

        return gamma_peaks

    def get_energy_key(self, isotope_data, energy_value, tol=0.001):
        """Find the key in isotope_data corresponding to energy_value within a tolerance"""
        for key in isotope_data:
            try:
                if abs(float(key) - energy_value) < tol:
                    return key
            except ValueError:
                continue
        return None

    def update_experimental_data(self, domain, energy_value, efficiency, efficiency_uncertainty):
        """Update the experimental data with calculated efficiency"""
        for entry in self.experimental_data:
            if entry['domain'] == domain and self.source_name in entry:
                isotope_data = entry[self.source_name]
                key = self.get_energy_key(isotope_data, energy_value, tol=0.001)
                if key:
                    print(f"Updating efficiency for domain {domain}, energy {key}")
                    # Store both efficiency and uncertainty
                    self.efficiencies.append((float(key), efficiency, efficiency_uncertainty))
                    isotope_data[key]['eff'] = [efficiency, efficiency_uncertainty]
                else:
                    print(f"Energy {energy_value} not found in isotope_data for domain {domain}.")



    def save_experimental_data(self, file_path):
        """Save the updated experimental data to the original file"""
        with open(file_path, 'w') as f:
            json.dump(self.experimental_data, f, indent=2)
        print(f"Updated experimental data saved to {file_path}")

    def plot_efficiencies(self):
        """Plot the efficiencies with their uncertainties using improved error visualization"""
        if not self.efficiencies:
            print("No efficiency data available to plot.")
            return

        # Convert data to numpy arrays for easier manipulation
        energies = np.array([energy for energy, _, _ in self.efficiencies])
        efficiencies = np.array([eff for _, eff, _ in self.efficiencies])
        uncertainties = np.array([unc for _, _, unc in self.efficiencies])

        # Create figure and axis objects with a certain size
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the main data points with error bars
        ax.errorbar(energies, efficiencies, yerr=uncertainties, 
                   fmt='o', color='blue', capsize=5, capthick=1,
                   elinewidth=1, markersize=6, label='Measured Efficiency')

        # Add semi-transparent confidence band


        # Customize the plot
        ax.set_xlabel('Energy (keV)', fontsize=12)
        ax.set_ylabel('Efficiency', fontsize=12)
        ax.set_title('Detector Efficiency vs Energy', fontsize=14)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Use log scale for better visualization of the efficiency curve
        ax.set_xscale('log')
        ax.set_yscale('log')

        # Set major and minor grid for y-axis
        ax.yaxis.set_major_formatter(plt.ScalarFormatter())
        ax.yaxis.set_minor_formatter(plt.ScalarFormatter())
        ax.yaxis.set_major_locator(plt.LogLocator(base=10.0))
        ax.yaxis.set_minor_locator(plt.LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1))
        ax.grid(True, which='major', linestyle='-', alpha=0.5)
        ax.grid(True, which='minor', linestyle=':', alpha=0.2)

        # Ensure y-axis ticks are visible
        ax.tick_params(axis='y', which='both', labelsize=10)
        
        # Add legend
        ax.legend(fontsize=10)

        # Adjust layout to prevent label clipping
        plt.tight_layout()

        # Show the plot
        plt.show()

        # Print summary statistics
        print(f"\nEfficiency Analysis Summary:")
        print(f"Number of data points: {len(self.efficiencies)}")
        print(f"Energy range: {min(energies):.1f} - {max(energies):.1f} keV")
        print(f"Average efficiency: {np.mean(efficiencies):.2e}")
        print(f"Average uncertainty: {np.mean(uncertainties):.2e}")