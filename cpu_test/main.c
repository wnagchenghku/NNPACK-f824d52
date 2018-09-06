#include <stdio.h>
#include <stdlib.h>
#include <malloc.h> /* memalign */
#include <string.h>
#include <nnpack.h>


void convolution()
{
	sleep(2);
	char memoryBuffer[16384 * 500];
	size_t memorySize = 16384 * 500;
	enum nnp_status init_status = nnp_initialize(&memset, &malloc, &free);
	if (init_status != nnp_status_success) {
		printf("NNPACK initialization failed: error code %d\n", init_status);
		exit(1);
	}
	printf("NNPACK init true\n");

	const size_t batch_size = 1;
	const size_t input_channels = 16;
	const size_t output_channels = 16;
	const struct nnp_padding input_padding = {0, 0, 0, 0};
	const struct nnp_size input_size = {180, 180};
	const struct nnp_size kernel_size = {3, 3}; // nnp_convolution_algorithm_ft16x16
	
	// const struct nnp_size kernel_size = {1, 1}; // nnp_convolution_algorithm_direct

	const struct nnp_size output_subsampling = {1, 1};
	const struct nnp_size output_size = {
		.width = (input_padding.left + input_size.width + input_padding.right - kernel_size.width) / output_subsampling.width + 1,
		.height = (input_padding.top + input_size.height + input_padding.bottom - kernel_size.height) / output_subsampling.height + 1
	};
	void* input = malloc(batch_size * input_channels * input_size.width * input_size.height * sizeof(float));
	void* kernel = malloc(input_channels * output_channels * kernel_size.width * kernel_size.height * sizeof(float));
	void* output = malloc(batch_size * output_channels * output_size.width * output_size.height * sizeof(float));
	void* bias = malloc(output_channels * sizeof(float));

	memset(input, 0, batch_size * input_channels * input_size.width * input_size.height * sizeof(float));
	memset(kernel, 0, input_channels * output_channels * kernel_size.width * kernel_size.height * sizeof(float));
	memset(output, 0, batch_size * output_channels * output_size.width * output_size.height * sizeof(float));
	memset(bias, 0, output_channels * sizeof(float));

	enum nnp_convolution_algorithm algorithm = nnp_convolution_algorithm_auto;
	enum nnp_convolution_transform_strategy transform_strategy = nnp_convolution_transform_strategy_compute;
	enum nnp_status status = nnp_status_success;

	status = nnp_convolution_inference(
			algorithm, transform_strategy,
			input_channels, output_channels,
			input_size, input_padding, kernel_size, output_subsampling,
			input, kernel, bias, output,
			memoryBuffer, &memorySize,
			nnp_activation_identity, NULL,
			NULL,
			NULL);

	if (status != nnp_status_success) {
		printf("NNPACK nnp_convolution_inference failed: error code %d\n", status);
		exit(1);
	}
	int i;
	printf("[");
	for (i = 0; i < batch_size * output_channels * output_size.width * output_size.height; ++i) {
		//if (i != 0) printf(", ");
		//printf("%f", *((float*)output + i));
	}
	printf("]\n");
	printf("nnp convolution!\n");
}

void fully_connected()
{
	enum nnp_status status = nnp_initialize(&memset, &malloc, &free);
	if (status != nnp_status_success) {
		printf("NNPACK initialization failed: error code %d\n", status);
		exit(1);
	}

	const size_t batch_size = 1;
	const size_t input_channels = 4;
	const size_t output_channels = 4;

	void* input = malloc(batch_size * input_channels * sizeof(float));
	void* kernel = malloc(input_channels * output_channels * sizeof(float));
	void* output = malloc(batch_size * output_channels * sizeof(float));

	memset(input, 0, batch_size * input_channels * sizeof(float));
	memset(kernel, 0, input_channels * output_channels * sizeof(float));
	memset(output, 0, batch_size * output_channels * sizeof(float));
	// f32
	status = nnp_fully_connected_inference(input_channels, output_channels, input, kernel, output, NULL);
	if (status != nnp_status_success) {
		printf("NNPACK nnp_fully_connected_inference failed: error code %d\n", status);
		exit(1);
	}
	printf("nnp_fully_connected_inference!\n");
}

int main(int argc, char *argv[])
{
	convolution();
	fully_connected();
	sleep(2);
	return 0;
}