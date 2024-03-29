<a name="readme-top"></a>

## About The Project

This project consists of an unmanned physics simulation of a fluid. This simulation is meant to be interactive, although this function will be limited, so that the user can play around with the fluid, and maybe even change it's color. This simulation is done using pygame and numpy to create particles that are affected by gravity, density, and pressure forces, utilizing knowledge of vector mathematics. The main strategies employed involve the calculation of a vector and density field which are calculated at each pixel of the window.

The 3 main objectives were the following:
1. Utilize smooth particle hydrodynamics approach for fluids
2. Simulate a fluid randomly flowing
3. Implement an interactive element (i.e click to place fluid, manipulate fluid by clicking it)

In this repository you will find the single main file for the fluid simulation itself, as well as files relating to the presentation and technical reports for the all iterations leading up to the final.

Use the `FluidSimMain.py` to use the program.


## Getting Started with the Program

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites and Installation

This program uses the following libraries:
* Numpy
* Math
* Pygame
* Time
  
To use numpy and pygame you must first install them into the git repository you are using. Below are the instructions to install this repository and use the program: 
1. Clone the repository
   ```sh
   git clone https://github.com/pablosabaterlp/EECE2140FinalProject.git
   ```
2. Install Numpy packages in IDE Terminal
   ```sh
   pip3 install numpy
   ```
3. Install pygame packages in IDE Terminal
   ```sh
   pip3 install pygame
   ```
4. Launch `FluidSimMain.py` and run to use. Refer to the following section for how to use it

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

The following actions can be performed in the program:
* SPACE - Start/Stop the animation
* P - Toggle visibility of the particles
* F - Toggle visibility of the density field
* B - Toggle visibility of the vector field
* T - Toggle the time delay to slow the motion
* G - Toggle the affect of gravity
* R - Toggle random forces on the particles
* V - Toggle the calculation of the vector field
* M - Add more particles to the window from the top left corner
* A - Toggle visbility of particle velocity
* LEFT CLICK - Grab particles in an area around cursor and move them around
* RIGHT CLICK - Push away particles from cursor

Demo:

![](https://github.com/pablosabaterlp/EECE2140FinalProject/blob/main/otherFiles/simulationgif.gif)
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributing

For all contributions to this project made by a non-collaborator, use the following steps. Collaborations are always welcome.

1. Fork the Project
2. Create the Branch
   ```sh
    git checkout -b BRANCHNAME
   ```
3. Commit your Changes
   ```sh
    git commit -m 'FEATURE ADDED'
   ```
4. Add the origin as this repository
   ```sh
    git remote add origin https://github.com/pablosabaterlp/EECE2140FinalProject.git
   ```
5. Push to the Branch
   ```sh
    git push -u origin BRANCHNAME
   ```
6. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

Authors:
* Pablo Sabater - Presentation, organization, comments, and help with coding
* Martin Alvo - Lead coder
  
* [Sebastian Lague Video (Inspiration)](https://www.youtube.com/watch?v=rSKMYc1CQHE&t=245s&ab_channel=SebastianLague)
* [SPH Wikipedia](https://en.wikipedia.org/wiki/Smoothed-particle_hydrodynamics)
* [Numpy N Dimensional Arrays](https://numpy.org/doc/stable/reference/arrays.ndarray.html)

<p align="right">(<a href="#readme-top">back to top</a>)</p>




