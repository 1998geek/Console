# vLLM 启动参数通俗说明 + 示例

本文件详细解释了 vLLM 常用启动参数的含义、作用和示例，适用于部署、调优和向量知识库应用。

---

## 1. block_size

- **含义**：每个内存块分配的大小，单位是 token。
- **作用**：控制显存的分配粒度。越小越灵活，越大性能可能更好。
- **示例**：
  ```bash
  --block-size 16
2. gpu_memory_utilization
含义：使用 GPU 显存的最大比例（0~1）。

作用：限制模型最多占用多少 GPU 显存，防止 OOM。

示例：

bash
复制
编辑
--gpu-memory-utilization 0.9
3. max_num_segs
含义：最大可用 segment 数量，用于预填充的任务切分。

作用：控制并发能力，适当调大可以提升吞吐，但增加显存压力。

示例：

bash
复制
编辑
--max-num-segs 512
4. max_model_len
含义：模型支持的最大上下文长度（token 数）。

作用：控制输入 + 输出的最大 token 数，超过可能报错。

示例：

bash
复制
编辑
--max-model-len 8192
5. guided_decoding_backend
含义：指定用于引导式生成的控制后端，如正则规则匹配等。

作用：使模型生成受控，更适用于结构化输出场景。

示例：

bash
复制
编辑
--guided-decoding-backend re2
6. scheduling_policy
含义：并发请求的调度策略。

作用：

FCFS: 先到先处理

LLM_ROUND_ROBIN: 多用户轮流生成，防止一人占满资源

示例：

bash
复制
编辑
--scheduling-policy LLM_ROUND_ROBIN
7. tensor_parallel_size
含义：张量并行 GPU 数。

作用：将模型切分后在多个 GPU 上并行推理。

示例：

bash
复制
编辑
--tensor-parallel-size 2
8. pipeline_parallel_size
含义：流水线并行的 GPU 数。

作用：适合超大模型部署，不同层放在不同 GPU 上。

示例：

bash
复制
编辑
--pipeline-parallel-size 4
9. enable_prefix_caching
含义：是否启用提示词前缀缓存。

作用：多个请求有相同前缀时加速处理，节省重复计算。

示例：

bash
复制
编辑
--enable-prefix-caching
10. enable_chunked_prefill
含义：是否启用 chunk 方式预填充。

作用：长输入分块处理，避免一次性占用大量显存。

示例：

bash
复制
编辑
--enable-chunked-prefill
11. enforce_eager
含义：启用 Eager 模式。

作用：立即执行每一步，不做优化调度；适合调试，性能低。

示例：

bash
复制
编辑
--enforce-eager
12. cpu_offload_gb
含义：允许将模型部分权重 offload 到 CPU 的最大 GB 数。

作用：节省显存，牺牲推理速度。

示例：

bash
复制
编辑
--cpu-offload-gb 4
13. disable_custom_all_reduce
含义：禁用 vLLM 自定义的 AllReduce 通信模块。

作用：用于张量并行的通信；禁用后使用默认方案，可能影响性能。

示例：

bash
复制
编辑
--disable-custom-all-reduce
14. limit_mm_per_prompt
含义：限制每个多模态请求使用的最大显存（MiB）。

作用：避免某些请求独占显存，提升系统稳定性。

示例：

bash
复制
编辑
--limit-mm-per-prompt 1024
15. model_quantization
含义：指定模型使用的量化精度。

作用：减少显存占用，加快推理；常见值有 int4、int8、fp16。

示例：

bash
复制
编辑
--model-quantization int4
16. mm_processor_kwargs
含义：图像预处理参数，JSON 格式传递。

作用：调整图像尺寸、裁剪等操作，适配模型要求。

示例：

bash
复制
编辑
--mm-processor-kwargs '{"resize": 224, "crop": 224}'
17. min_pixels
含义：多模态输入图像的最小像素数（宽 x 高）。

作用：防止输入图太小影响模型效果。

示例：

bash
复制
编辑
--min-pixels 1024
18. max_pixels
含义：多模态输入图像的最大像素数。

作用：限制输入图像尺寸，防止超大图导致内存溢出。

示例：

bash
复制
编辑
--max-pixels 1048576