import os
import nautilus
import pyexiv2
import gnomevfs

class PhotoRate(nautilus.MenuProvider, nautilus.ColumnProvider, nautilus.InfoProvider):
    SEPARATOR = u'\u2015' * 10
    RATING_KEY = "Exif.Image.Rating"
    
    IMAGE_MIME_TYPES = [
        "image/jpeg",
        "image/jpg",
        "image/x-dcraw",
        "image/gif",
        "image/tiff"
    ]

    def __init__(self):
        pass
    
    def get_columns(self):
        return nautilus.Column("PhotoRate::photo_rating",
                               "rating",
                               "Rating",
                               "Get/Set Photo Ratings"),

    def update_file_info(self, file):
        rating = ""
        if self.is_image_type(file):
            path = gnomevfs.get_local_path_from_uri(file.get_uri())
            
            try:
                image = pyexiv2.Image(path)
                image.readMetadata()
            
                if self.RATING_KEY in image.exifKeys():
                    rating = image[self.RATING_KEY]
                    file.add_emblem("photorate-%s" % int(rating))
                    
            except IOError, e:
                print e
        
        file.add_string_attribute("rating", self.rating_for_display(rating))

    def get_file_items(self, window, files):
        if len(files) == 0:
            return
        
        if not self.is_image_type(files[0]):
            return

        mainmenu = nautilus.MenuItem('PhotoRate::Rate', 'Rate It...', '')

        submenu = nautilus.Menu()
        mainmenu.set_submenu(submenu)

        menuitem = nautilus.MenuItem('PhotoRate::NoRating', 'No Rating', '')
        menuitem.connect("activate", self.save_rating, 0, files)
        submenu.append_item(menuitem)

        menuitem = nautilus.MenuItem('PhotoRate::SEP1', self.SEPARATOR, '')
        menuitem.set_property("sensitive", False)
        submenu.append_item(menuitem)

        menuitem = nautilus.MenuItem('PhotoRate::One', '*', '')
        menuitem.connect("activate", self.save_rating, 1, files)
        submenu.append_item(menuitem)

        menuitem = nautilus.MenuItem('PhotoRate::Two', '* *', '')
        menuitem.connect("activate", self.save_rating, 2, files)
        submenu.append_item(menuitem)

        menuitem = nautilus.MenuItem('PhotoRate::Three', '* * *', '')
        menuitem.connect("activate", self.save_rating, 3, files)
        submenu.append_item(menuitem)

        menuitem = nautilus.MenuItem('PhotoRate::Four', '* * * *', '')
        menuitem.connect("activate", self.save_rating, 4, files)
        submenu.append_item(menuitem)

        menuitem = nautilus.MenuItem('PhotoRate::Five', '* * * * *', '')
        menuitem.connect("activate", self.save_rating, 5, files)
        submenu.append_item(menuitem)

        return mainmenu,
        
    def get_background_items(self, window, file):
        return
    
    def save_rating(self, menu_item, rating, files):
        for file in files:
            if self.is_image_type(file):                    
                path = gnomevfs.get_local_path_from_uri(file.get_uri())
                
                try:
                    image = pyexiv2.Image(path)
                    image.readMetadata()
                    image[self.RATING_KEY] = rating
                    image.writeMetadata()
                    
                    file.invalidate_extension_info()
                except IOError, e:
                    print e

    def rating_for_display(self, rating):
        if rating == "":
            rating = 0
    
        return u'* ' * rating
    
    def is_image_type(self, file):
        return (file.get_uri_scheme() == 'file'
                and not file.is_directory()
                and file.get_mime_type() in self.IMAGE_MIME_TYPES)
