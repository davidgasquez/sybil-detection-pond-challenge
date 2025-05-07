.DEFAULT_GOAL := setup

.PHONY: .uv
.uv:
	@uv -V || echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/'

.PHONY: setup
setup: .uv
	uv sync --frozen

.PHONY: base-sybil-detection
base-sybil-detection:
	@echo "Downloading Base Sybil Detection Data"
	@mkdir -p data/raw/base
	@wget https://pond-open-files.cryptopond.xyz/frontier/others/Z8HgK3Pq/base_sybil_detection.zip -O /tmp/base_sybil_detection.zip
	@unzip /tmp/base_sybil_detection.zip -d /tmp/base_sybil_detection
	@cp -r /tmp/base_sybil_detection/competition_4712551_base/* data/raw/base/
	@rm -rf /tmp/base_sybil_detection.zip /tmp/base_sybil_detection

.PHONY: ethereum-sybil-detection
ethereum-sybil-detection:
	@echo "Downloading Ethereum Sybil Detection Data"
	@mkdir -p data/raw/ethereum
	@wget https://pond-open-files.cryptopond.xyz/frontier/others/X7GJ91Ld/ethereum_sybil_detection.zip -O /tmp/ethereum_sybil_detection.zip
	@unzip /tmp/ethereum_sybil_detection.zip -d /tmp/ethereum_sybil_detection
	@cp -r /tmp/ethereum_sybil_detection/competition_4712551_ethereum/* data/raw/ethereum/
	@rm -rf /tmp/ethereum_sybil_detection.zip /tmp/ethereum_sybil_detection

.PHONY: data
data: base-sybil-detection ethereum-sybil-detection
	@echo "All datasets downloaded successfully"
