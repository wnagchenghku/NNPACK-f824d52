import torch


PYTORCH_WEIGHTS_RELATIVE_PATH = "pytorch_weights.pkl"
PYTORCH_MODEL_RELATIVE_PATH = "pytorch_model.pkl"

trained_models = ['resnet18', 'densenet201']

def build_model(name,
	            model_data_path,
                base_image,
                container_registry=None,
                pkgs_to_install=None):

    run_cmd = ''
    if pkgs_to_install:
        run_as_lst = 'RUN apt-get -y install build-essential && pip install'.split(
            ' ')
        run_cmd = ' '.join(run_as_lst + pkgs_to_install)
    with tempfile.NamedTemporaryFile(
            mode="w+b", suffix="tar") as context_file:
        # Create build context tarfile
        with tarfile.TarFile(
                fileobj=context_file, mode="w") as context_tar:
            context_tar.add(model_data_path)
            # From https://stackoverflow.com/a/740854/814642
            try:
                df_contents = StringIO(
                    str.encode(
                        "FROM {container_name}\n{run_command}\nCOPY {data_path} /model/\n".
                        format(
                            container_name=base_image,
                            data_path=model_data_path,
                            run_command=run_cmd)))
                df_tarinfo = tarfile.TarInfo('Dockerfile')
                df_contents.seek(0, os.SEEK_END)
                df_tarinfo.size = df_contents.tell()
                df_contents.seek(0)
                context_tar.addfile(df_tarinfo, df_contents)
            except TypeError:
                df_contents = StringIO(
                    "FROM {container_name}\n{run_command}\nCOPY {data_path} /model/\n".
                    format(
                        container_name=base_image,
                        data_path=model_data_path,
                        run_command=run_cmd))
                df_tarinfo = tarfile.TarInfo('Dockerfile')
                df_contents.seek(0, os.SEEK_END)
                df_tarinfo.size = df_contents.tell()
                df_contents.seek(0)
                context_tar.addfile(df_tarinfo, df_contents)
        # Exit Tarfile context manager to finish the tar file
        # Seek back to beginning of file for reading
        context_file.seek(0)
        image = "{name}".format(name=name)
        if container_registry is not None:
            image = "{reg}/{image}".format(
                reg=container_registry, image=image)
        docker_client = docker.from_env()
        self.logger.info(
            "Building model Docker image with model data from {}".format(
                model_data_path))
        image_result, build_logs = docker_client.images.build(
            fileobj=context_file, custom_context=True, tag=image)
        for b in build_logs:
            if 'stream' in b and b['stream'] != '\n':  #log build steps only
                self.logger.info(b['stream'].rstrip())

    return image

def serialize_object(obj):
    s = StringIO()
    c = CloudPickler(s, 2)
    c.dump(obj)
    return s.getvalue()

def save_python_function(name, func):
    # predict_fname = "func.pkl"

    # Serialize function
    # s = StringIO()
    # c = CloudPickler(s, 2)
    # c.dump(func)
    # serialized_prediction_function = s.getvalue()

    # Set up serialization directory
    serialization_dir = os.path.abspath(tempfile.mkdtemp(suffix='clipper'))
    logger.info("Saving function to {}".format(serialization_dir))

    # Write out function serialization
    # func_file_path = os.path.join(serialization_dir, predict_fname)
    # if sys.version_info < (3, 0):
    #     with open(func_file_path, "w") as serialized_function_file:
    #         serialized_function_file.write(serialized_prediction_function)
    # else:
    #     with open(func_file_path, "wb") as serialized_function_file:
    #         serialized_function_file.write(serialized_prediction_function)
    # logging.info("Serialized and supplied predict function")
    return serialization_dir

def deploy_pytorch_model(pytorch_model):
	serialization_dir = save_python_function(name, func)

    # save Torch model
    torch_weights_save_loc = os.path.join(serialization_dir,
                                          PYTORCH_WEIGHTS_RELATIVE_PATH)

    torch_model_save_loc = os.path.join(serialization_dir,
                                        PYTORCH_MODEL_RELATIVE_PATH)

    try:
        torch.save(pytorch_model.state_dict(), torch_weights_save_loc)
        serialized_model = serialize_object(pytorch_model)
        with open(torch_model_save_loc, "wb") as serialized_model_file:
            serialized_model_file.write(serialized_model)

        # Deploy model
        build_and_deploy_model(
            name, version, input_type, serialization_dir, base_image, labels,
            registry, pkgs_to_install)

    except Exception as e:
        raise Exception("Error saving torch model: %s" % e)

def main():

	for model in trained_models:
		deploy_pytorch_model(getattr(models, model)())


if __name__ == '__main__':
	main()