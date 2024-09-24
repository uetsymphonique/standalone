# MITRE Caldera Plugin: Standalone

A plugin supplying Caldera with auto-generating standalone agent for running adversary 

# Installation

Using the Standalone plugin with Caldera will enable users to auto-generate standalone agent to run test cases in Caldera's adversary plan

To run Caldera along with the Standalone plugin:
1. Download Caldera as detailed in the [Installation Guide](https://github.com/mitre/Caldera)
2. Enable the Standalone plugin by adding `- standalone` to the list of enabled plugins in `conf/local.yml` or `conf/default.yml` (if running Caldera in insecure mode)
3. Start Caldera 

# Additional setup
Each emulation plan will have an adversary and a set of facts. Please ensure to select the related facts to the 
adversary when starting an operation. 

Downloading function that downloads compressed file requires installation of `aiofiles`. It can be installed by using the following:

`pip3 install aiofiles`
