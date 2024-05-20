
<!-- Much thanks to https://github.com/othneildrew/Best-README-Template for the template -->
<!-- And to https://github.com/alexandresanlim/Badges4-README.md-Profile for the badges -->
<img id="top" src="https://i.imgur.com/iW7JeHC.png" width="200" align="right" />

Distributed Image Processing System using Cloud Computing

  
###### This is a _Distributed Image Processing System using Cloud Computing_; the major task project for the **CSE354 - Distributed Computing** course in the Faculty of Engineering, Ain Shams University; for Spring 2024.

<details>
  <summary><b>Table of Contents</b></summary>
	<ol>
		<li><a href="#system-architecture">System Architecture</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#libraries-and-dependencies">Libraries and Dependencies</a></li>
		<li><a href="#environment-variables">Environment Variables</a></li>
		<li><a href="#usage-instructions">Usage Instructions</a></li>
		<li><a href="#upload-images">Upload Images</a></li>
	</ol>
</details>



## System Architecture
The system consists of the following components:

<ol>
  <li>Client: Manages user interactions, uploads images, and queries task statuses.</li>
  <li>Master: Receives tasks from the client, manages task distribution, and communicates with worker nodes.</li>
  <li>Worker: Processes images according to the specified operations and uploads the results to Azure Blob Storage.</li>
</ol>


## Features
<ul>
  <li>Edge detection</li>
  <li>Color inversion</li>
  <li>Gaussian blur</li>
  <li>Image sharpening</li>
  <li>Grayscale conversion</li>
  <li>Brightness adjustment</li>
</ul>

<p align="right">(<a href="#top">back to top</a>)</p>

## Libraries and Dependencies

  ```sh
  pip install flask requests opencv-python numpy azure-storage-blob azure-storage-queue
  ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Environment Variables
```sh
AZURE_STORAGE_CONNECTION_STRING="YourAzureStorageConnectionString"
```
<p align="right">(<a href="#top">back to top</a>)</p>

## Usage Instructions

Each file is independant so you can run them in whichever order you want 

```sh
python client.py
```
```sh
python master_node.py
```
```sh
python worker_thread.py
```

<p align="right">(<a href="#top">back to top</a>)</p>

## Upload Images
<ul>
  <li>Open your browser and navigate to the client node's address (e.g., http://localhost:8000).</li>
  <li>Use the provided web interface to upload images and select the desired image processing operation.</li>
</ul>

<p align="right">(<a href="#top">back to top</a>)</p>

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.
If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>


###### Distributed under the  GPL-3.0 License. See [`LICENSE`](/LICENSE) for more information.

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/vadrif-draco/asufecse483project-simpleperceptionstack.svg?style=for-the-badge
[contributors-url]: https://github.com/vadrif-draco/asufecse483project-simpleperceptionstack/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/vadrif-draco/asufecse483project-simpleperceptionstack.svg?style=for-the-badge
[forks-url]: https://github.com/vadrif-draco/asufecse483project-simpleperceptionstack/network/members
[stars-shield]: https://img.shields.io/github/stars/vadrif-draco/asufecse483project-simpleperceptionstack.svg?style=for-the-badge
[stars-url]: https://github.com/vadrif-draco/asufecse483project-simpleperceptionstack/stargazers
[issues-shield]: https://img.shields.io/github/issues/vadrif-draco/asufecse483project-simpleperceptionstack.svg?style=for-the-badge
[issues-url]: https://github.com/vadrif-draco/asufecse483project-simpleperceptionstack/issues

[python-shield]: https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue
[python-url]: https://www.python.org/
[opencv-shield]: https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white
[opencv-url]: https://opencv.org/
[numpy-shield]: https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white
[numpy-url]: https://numpy.org/
[pandas-shield]: https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white
[pandas-url]: https://pandas.pydata.org/
[jupyter-shield]:	https://img.shields.io/badge/Jupyter-e46e32.svg?&style=for-the-badge&logo=Jupyter&logoColor=white
[jupyter-url]: https://jupyter.org/
[colab-shield]: https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252
[colab-url]: https://colab.research.google.com/

[before-vision]: assets/test_images/test5.jpg
