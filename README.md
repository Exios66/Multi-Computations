# Multi-Computations

A comprehensive framework for multimodal data analysis and processing, focusing on EEG, gaze tracking, and working memory task computations.

## Overview

This project provides a suite of tools and utilities for processing and analyzing multiple types of experimental data, specifically designed for cognitive science and neuroscience research. It includes modules for:

- EEG data processing and analysis
- Gaze tracking data processing
- Working memory task computations
- Synthetic data generation for testing
- Comprehensive reporting tools

## Project Structure

```
.
├── docs/               # Documentation files
├── src/               # Source code
│   ├── EEG-Py/       # EEG processing modules
│   ├── Gaze-Python/  # Gaze tracking analysis
│   ├── WM-Tasks/     # Working memory task implementations
│   ├── python/       # Core Python utilities and reporting
│   └── utility/      # Common utility functions
├── testing/          # Test files and test data
└── requirements.txt  # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Multi-Computations.git
cd Multi-Computations
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- Dependencies listed in requirements.txt:
  - pandas >= 1.3.0
  - numpy >= 1.20.0
  - matplotlib >= 3.4.0
  - scipy >= 1.7.0
  - mne >= 0.23.0
  - scikit-learn >= 0.24.0
  - And more...

## Usage

Each component has its own specific usage instructions. Please refer to the README files in each subdirectory for detailed information:

- [EEG Processing](src/EEG-Py/README.md)
- [Gaze Tracking](src/Gaze-Python/README.md)
- [Working Memory Tasks](src/WM-Tasks/README.md)
- [Reporting Tools](src/python/README.md)

## Testing

The project includes comprehensive test suites and synthetic data generation for testing purposes:

```bash
python test_synthetic.py  # Run synthetic data tests
python -m pytest testing/ # Run all tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Contact

For questions and support, please open an issue in the GitHub repository.
