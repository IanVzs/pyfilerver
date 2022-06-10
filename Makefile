# Minimal makefile for Sphinx documentation
.PHONY: help

# Put it first so that "make" without argument is like "make help".
help: # 获取命令行示例
	@grep ":" Makefile | grep -v "Makefile"

run: # 运行
	pip install .
	pyfilerver
