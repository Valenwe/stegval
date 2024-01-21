import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

class ImageDisplayer:
    def __init__(self, image, figsize=(6, 8)):
        self.fig, self.ax1 = plt.subplots(1, 1, figsize=figsize)

        # Initialize with blank data
        width, height = image.size
        self.image_array = np.zeros((height, width), dtype=np.uint8)
        self.pil_img = Image.fromarray(self.image_array, mode='L')
        self.img = self.ax1.imshow(self.pil_img, vmin=0, vmax=255, interpolation="None", cmap="gray")

        self.fig.canvas.draw()

        # Cache the background
        self.axbackground = self.fig.canvas.copy_from_bbox(self.ax1.bbox)

        plt.show(block=False)

    def refresh_image(self, image_array):
        # Convert to NumPy array if it's a Pillow image
        if isinstance(image_array, Image.Image):
            image_array = np.array(image_array)

        # Ensure the image is in RGB format
        if image_array.ndim == 2:
            # If 2D, convert to RGB by duplicating the single channel
            image_array = np.stack((image_array,) * 3, axis=-1)
        elif image_array.shape[2] == 1:
            # If 3D with a single channel, duplicate the channel to create RGB
            image_array = np.concatenate((image_array,) * 3, axis=-1)

        # Initialize with a blank PIL image
        self.pil_img = Image.fromarray(image_array, mode='RGB')
        self.img.set_array(np.array(self.pil_img))

        self.ax1.draw_artist(self.img)

        self.fig.canvas.blit(self.ax1.bbox)
        self.fig.canvas.flush_events()
        plt.pause(0.01)  # Give the GUI event loop time to process events

    def close_plot(self):
        plt.close()

# Example usage
if __name__ == "__main__":
    displayer = ImageDisplayer()

    # Display the initial image
    initial_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    displayer.refresh_image(initial_image)
    input()

    # Update the displayed image
    updated_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    displayer.refresh_image(updated_image)
    input()

    # Close the plot
    displayer.close_plot()
