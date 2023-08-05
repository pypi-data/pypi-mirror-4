#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Tue 19 Jul 2011 12:53:56 CEST 


class BoundingBox:
  """Defines a bounding box object"""

  def __init__(self, x, y, width, height):
    """Initializes the bounding box object with the following configuration:

       x: upper left x coordinate
       y: upper left y coordinate
       width: total bounding box width in pixels
       height: total bounding box height in pixels
    """
    self.x = int(x)
    self.y = int(y)
    self.width = int(width)
    self.height = int(height)

  def area(self):
    return self.width * self.height

  def coordinates(self):
    """Returns the 4 coordinates of the bounding box: top-left, top-right,
    bottom-left, bottom-right."""
    return (
        (self.x, self.y),
        (self.x+self.width, self.y),
        (self.x, self.y+self.height),
        (self.x+self.width, self.y + self.height),
        )

  def is_valid(self,faceSizeFilter=0):
    """
     Determines if a certain bounding box is valid

     Two conditions for a valid face bounding box
      - The bounding box is greater than zero
      - The bounding box is greater than faceSizeFilter

    """
    if(faceSizeFilter>0):
      return (self.height > faceSizeFilter)
    else:
      return bool(self.x + self.width + self.y + self.height)

  def __str__(self):
    return "(%d+%d,%d+%d)" % (self.x, self.width, self.y, self.height)

  def __repr__(self):
    return "<BoundingBox: %s>" % str(self)

  def draw(self, image, thickness=2, color=(255,0,0)):
    """Draws a bounding box on a given image. If the image is colored, it is
    considered to be RGB in the Torch standard image representation, otherwise,
    we first convert the color into grayscale to then apply the bounding
    box."""

    if image.rank() == 2: #grayscale
      if isinstance(color, (tuple, list)):
        color = bob.ip.rgb_to_gray_u8(*color)

    # draws one line for each size of the bounding box
    for k in range(thickness):
      bob.ip.draw_box(image, self.x-k, self.y-k, self.width+2*k, 
          self.height+2*k)

