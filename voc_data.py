import tensorflow as tf
import os
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
import random

from box_utils import compute_target
from image_utils import random_patching, horizontal_flip
from functools import partial

class Custom_find_area_Dataset():
    """ Class for VOC Dataset

    Attributes:
        root_dir: dataset root dir (ex: ./data/VOCdevkit)
        year: dataset's year (2007 or 2012)
        num_examples: number of examples to be used
                      (in case one wants to overfit small data)
    """

    def __init__(self, root_dir, 
                 new_size, num_examples=-1, augmentation=None):
        super(Custom_find_area_Dataset, self).__init__()
        self.idx_to_name = [
            'text_area'
             ]
        self.name_to_idx = dict([(v, k)
                                 for k, v in enumerate(self.idx_to_name)])

        self.data_dir = root_dir
        self.image_dir = os.path.join(self.data_dir, 'PNGImages')
        self.anno_dir = os.path.join(self.data_dir, 'Annotations')
        self.ids = list(map(lambda x: x[:-4], os.listdir(self.image_dir)))
        self.new_size = new_size

        if num_examples != -1:
            self.ids = self.ids[:num_examples]

        self.train_ids = self.ids[:int(len(self.ids) * 0.75)]
        self.val_ids = self.ids[int(len(self.ids) * 0.75):]

        if augmentation == None:
            self.augmentation = ['original']
        else:
            self.augmentation = augmentation + ['original']

    def __len__(self):
        return len(self.ids)

    def _get_image(self, index):
        """ Method to read image from file
            then resize to (300, 300)
            then subtract by ImageNet's mean
            then convert to Tensor

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (3, 300, 300)
        """
        filename = self.ids[index]
        img_path = os.path.join(self.image_dir, filename + '.jpg')
        img = Image.open(img_path)

        return img

    def _get_annotation(self, index, orig_shape):
        """ Method to read annotation from file
            Boxes are normalized to image size
            Integer labels are increased by 1

        Args:
            index: the index to get filename from self.ids
            orig_shape: image's original shape

        Returns:
            boxes: numpy array of shape (num_gt, 4)
            labels: numpy array of shape (num_gt,)
        """
        h, w = orig_shape
        filename = self.ids[index]
        anno_path = os.path.join(self.anno_dir, filename + '.xml')
        objects = ET.parse(anno_path).findall('object')
        boxes = []
        labels = []

        for obj in objects:
            name = obj.find('name').text.lower().strip()
            bndbox = obj.find('bndbox')
            xmin = (float(bndbox.find('xmin').text) - 1) / w
            ymin = (float(bndbox.find('ymin').text) - 1) / h
            xmax = (float(bndbox.find('xmax').text) - 1) / w
            ymax = (float(bndbox.find('ymax').text) - 1) / h
            boxes.append([xmin, ymin, xmax, ymax])

            if name not in self.name_to_idx.keys() :
                print("Doesn't exist Key value in self.name_to_idx.keys() !! ")
            else :
                labels.append(self.name_to_idx[name] + 1)

        return np.array(boxes, dtype=np.float32), np.array(labels, dtype=np.int64)

    def generate(self, subset=None):
        """ The __getitem__ method
            so that the object can be iterable

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (300, 300, 3)
            boxes: tensor of shape (num_gt, 4)
            labels: tensor of shape (num_gt,)
        """
        if subset == 'train':
            indices = self.train_ids
        elif subset == 'val':
            indices = self.val_ids
        else:
            indices = self.ids
        for index in range(len(indices)):
            # img, orig_shape = self._get_image(index)
            filename = indices[index]
            img = self._get_image(index)
            w, h = img.size
            boxes, labels = self._get_annotation(index, (h, w))
            boxes = tf.constant(boxes, dtype=tf.float32)
            labels = tf.constant(labels, dtype=tf.int64)

            augmentation_method = np.random.choice(self.augmentation)
            if augmentation_method == 'patch':
                img, boxes, labels = random_patching(img, boxes, labels)
            elif augmentation_method == 'flip':
                img, boxes, labels = horizontal_flip(img, boxes, labels)

            img = np.array(img.resize(
                (self.new_size, self.new_size)), dtype=np.float32)
            img = (img / 127.0) - 1.0
            img = tf.constant(img, dtype=tf.float32)


            yield filename, img
            
class CustomDataset_area():
    """ Class for VOC Dataset

    Attributes:
        root_dir: dataset root dir (ex: ./data/VOCdevkit)
        year: dataset's year (2007 or 2012)
        num_examples: number of examples to be used
                      (in case one wants to overfit small data)
    """

    def __init__(self, root_dir, default_boxes,
                 new_size, num_examples=-1, augmentation=None):
        super(CustomDataset_area, self).__init__()
        self.idx_to_name = [
            'text_area'
             ]
        self.name_to_idx = dict([(v, k)
                                 for k, v in enumerate(self.idx_to_name)])

        self.data_dir = root_dir
        self.image_dir = os.path.join(self.data_dir, 'PNGImages')
        self.anno_dir = os.path.join(self.data_dir, 'Annotations')
        self.ids = list(map(lambda x: x[:-4], os.listdir(self.image_dir)))
        self.default_boxes = default_boxes
        self.new_size = new_size

        if num_examples != -1:
            self.ids = self.ids[:num_examples]

        self.train_ids = self.ids[:int(len(self.ids) * 0.75)]
        self.val_ids = self.ids[int(len(self.ids) * 0.75):]

        if augmentation == None:
            self.augmentation = ['original']
        else:
            self.augmentation = augmentation + ['original']

    def __len__(self):
        return len(self.ids)

    def _get_image(self, index):
        """ Method to read image from file
            then resize to (300, 300)
            then subtract by ImageNet's mean
            then convert to Tensor

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (3, 300, 300)
        """
        filename = self.ids[index]
        img_path = os.path.join(self.image_dir, filename + '.jpg')
        img = Image.open(img_path)

        return img

    def _get_annotation(self, index, orig_shape):
        """ Method to read annotation from file
            Boxes are normalized to image size
            Integer labels are increased by 1

        Args:
            index: the index to get filename from self.ids
            orig_shape: image's original shape

        Returns:
            boxes: numpy array of shape (num_gt, 4)
            labels: numpy array of shape (num_gt,)
        """
        h, w = orig_shape
        filename = self.ids[index]
        anno_path = os.path.join(self.anno_dir, filename + '.xml')
        objects = ET.parse(anno_path).findall('object')
        boxes = []
        labels = []
        

        
        for obj in objects:
            name = obj.find('name').text.lower().strip()
            bndbox = obj.find('bndbox')
            xmin = (float(bndbox.find('xmin').text) - 1) / w
            ymin = (float(bndbox.find('ymin').text) - 1) / h
            xmax = (float(bndbox.find('xmax').text) - 1) / w
            ymax = (float(bndbox.find('ymax').text) - 1) / h
            boxes.append([xmin, ymin, xmax, ymax])
            
            if name not in self.name_to_idx.keys() :                
                print("Doesn't exist Key value in self.name_to_idx.keys() !! ")
                print("This file name is : ", anno_path )
            else :
                labels.append(self.name_to_idx[name] + 1)
        
        return np.array(boxes, dtype=np.float32), np.array(labels, dtype=np.int64)

    def generate(self, subset=None):
        """ The __getitem__ method
            so that the object can be iterable

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (300, 300, 3)
            boxes: tensor of shape (num_gt, 4)
            labels: tensor of shape (num_gt,)
        """
        if subset == 'train':
            indices = self.train_ids
        elif subset == 'val':
            indices = self.val_ids
        else:
            indices = self.ids
        for index in range(len(indices)):
            # img, orig_shape = self._get_image(index)
            filename = indices[index]
            img = self._get_image(index)
            w, h = img.size
            boxes, labels = self._get_annotation(index, (h, w))
            boxes = tf.constant(boxes, dtype=tf.float32)
            labels = tf.constant(labels, dtype=tf.int64)

            augmentation_method = np.random.choice(self.augmentation)
            if augmentation_method == 'patch':
                img, boxes, labels = random_patching(img, boxes, labels)
            elif augmentation_method == 'flip':
                img, boxes, labels = horizontal_flip(img, boxes, labels)

            img = np.array(img.resize(
                (self.new_size, self.new_size)), dtype=np.float32)
            img = (img / 127.0) - 1.0
            img = tf.constant(img, dtype=tf.float32)

            gt_confs, gt_locs = compute_target(
                self.default_boxes, boxes, labels)

            yield filename, img, gt_confs, gt_locs

class CustomDataset():
    """ Class for VOC Dataset

    Attributes:
        root_dir: dataset root dir (ex: ./data/VOCdevkit)
        year: dataset's year (2007 or 2012)
        num_examples: number of examples to be used
                      (in case one wants to overfit small data)
    """

    def __init__(self, root_dir, default_boxes,
                 new_size, num_examples=-1, augmentation=None):
        super(CustomDataset, self).__init__()
        self.idx_to_name = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
             '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
             '31', '32', '33', '34', '35', '36', '42', '43', '44', '45'
             ]
        self.name_to_idx = dict([(v, k)
                                 for k, v in enumerate(self.idx_to_name)])

        self.data_dir = root_dir
        self.image_dir = os.path.join(self.data_dir, 'PNGImages')
        self.anno_dir = os.path.join(self.data_dir, 'Annotations')
        self.ids = list(map(lambda x: x[:-4], os.listdir(self.image_dir)))
        self.default_boxes = default_boxes
        self.new_size = new_size

        if num_examples != -1:
            self.ids = self.ids[:num_examples]

        self.train_ids = self.ids[:int(len(self.ids) * 0.75)]
        self.val_ids = self.ids[int(len(self.ids) * 0.75):]

        if augmentation == None:
            self.augmentation = ['original']
        else:
            self.augmentation = augmentation + ['original']

    def __len__(self):
        return len(self.ids)

    def _get_image(self, index):
        """ Method to read image from file
            then resize to (300, 300)
            then subtract by ImageNet's mean
            then convert to Tensor

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (3, 300, 300)
        """
        filename = self.ids[index]
        img_path = os.path.join(self.image_dir, filename + '.png')
        img = Image.open(img_path)

        return img

    def _get_annotation(self, index, orig_shape):
        """ Method to read annotation from file
            Boxes are normalized to image size
            Integer labels are increased by 1

        Args:
            index: the index to get filename from self.ids
            orig_shape: image's original shape

        Returns:
            boxes: numpy array of shape (num_gt, 4)
            labels: numpy array of shape (num_gt,)
        """
        h, w = orig_shape
        filename = self.ids[index]
        anno_path = os.path.join(self.anno_dir, filename + '.xml')
        objects = ET.parse(anno_path).findall('object')
        boxes = []
        labels = []
        

        
        for obj in objects:
            name = obj.find('name').text.lower().strip()
            bndbox = obj.find('bndbox')
            xmin = (float(bndbox.find('xmin').text) - 1) / w
            ymin = (float(bndbox.find('ymin').text) - 1) / h
            xmax = (float(bndbox.find('xmax').text) - 1) / w
            ymax = (float(bndbox.find('ymax').text) - 1) / h
            boxes.append([xmin, ymin, xmax, ymax])
            
            if name not in self.name_to_idx.keys() :                
                print("Doesn't exist Key value in self.name_to_idx.keys() !! ")
                print("This file name is : ", anno_path )
            else :
                labels.append(self.name_to_idx[name] + 1)
        
        return np.array(boxes, dtype=np.float32), np.array(labels, dtype=np.int64)

    def generate(self, subset=None):
        """ The __getitem__ method
            so that the object can be iterable

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (300, 300, 3)
            boxes: tensor of shape (num_gt, 4)
            labels: tensor of shape (num_gt,)
        """
        if subset == 'train':
            indices = self.train_ids
        elif subset == 'val':
            indices = self.val_ids
        else:
            indices = self.ids
        for index in range(len(indices)):
            # img, orig_shape = self._get_image(index)
            filename = indices[index]
            img = self._get_image(index)
            w, h = img.size
            boxes, labels = self._get_annotation(index, (h, w))
            boxes = tf.constant(boxes, dtype=tf.float32)
            labels = tf.constant(labels, dtype=tf.int64)

            augmentation_method = np.random.choice(self.augmentation)
            if augmentation_method == 'patch':
                img, boxes, labels = random_patching(img, boxes, labels)
            elif augmentation_method == 'flip':
                img, boxes, labels = horizontal_flip(img, boxes, labels)

            img = np.array(img.resize(
                (self.new_size, self.new_size)), dtype=np.float32)
            img = (img / 127.0) - 1.0
            img = tf.constant(img, dtype=tf.float32)

            gt_confs, gt_locs = compute_target(
                self.default_boxes, boxes, labels)

            yield filename, img, gt_confs, gt_locs
            
            
class CustomDataset_for_test():
    """ Class for VOC Dataset

    Attributes:
        root_dir: dataset root dir (ex: ./data/VOCdevkit)
        year: dataset's year (2007 or 2012)
        num_examples: number of examples to be used
                      (in case one wants to overfit small data)
    """

    def __init__(self, root_dir, default_boxes,
                 new_size, num_examples=-1, augmentation=None):
        super(CustomDataset_for_test, self).__init__()
        self.idx_to_name = [
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18',
             '19', '20', '21', '22', '23', '24', '25', '26', '27', '28',
             '31', '32', '33', '34', '35', '36', '42', '43', '44', '45'
             ]
        self.name_to_idx = dict([(v, k)
                                 for k, v in enumerate(self.idx_to_name)])

        self.data_dir = root_dir
        self.image_dir = os.path.join(self.data_dir, 'PNGImages')
        print("image_dir : ", self.image_dir)
        self.ids = list(map(lambda x: x[:-5], os.listdir(self.image_dir)))
        self.default_boxes = default_boxes
        self.new_size = new_size

        if num_examples != -1:
            self.ids = self.ids[:num_examples]

        self.train_ids = self.ids[:int(len(self.ids) * 0.75)]
        self.val_ids = self.ids[int(len(self.ids) * 0.75):]

        if augmentation == None:
            self.augmentation = ['original']
        else:
            self.augmentation = augmentation + ['original']

    def __len__(self):
        return len(self.ids)

    def _get_image(self, index):
        """ Method to read image from file
            then resize to (300, 300)
            then subtract by ImageNet's mean
            then convert to Tensor

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (3, 300, 300)
        """
        filename = self.ids[index]
        img_path = os.path.join(self.image_dir, filename + '.jpeg')
        img = Image.open(img_path)

        return img



    def generate(self, subset=None):
        """ The __getitem__ method
            so that the object can be iterable

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (300, 300, 3)
            boxes: tensor of shape (num_gt, 4)
            labels: tensor of shape (num_gt,)
        """
        if subset == 'train':
            indices = self.train_ids
        elif subset == 'val':
            indices = self.val_ids
        else:
            indices = self.ids
        for index in range(len(indices)):
            # img, orig_shape = self._get_image(index)
            filename = indices[index]
            img = self._get_image(index)
            w, h = img.size
 

            img = np.array(img.resize(
                (self.new_size, self.new_size)), dtype=np.float32)
            img = (img / 127.0) - 1.0
            img = tf.constant(img, dtype=tf.float32)

            yield filename, img


class VOCDataset():
    """ Class for VOC Dataset

    Attributes:
        root_dir: dataset root dir (ex: ./data/VOCdevkit)
        year: dataset's year (2007 or 2012)
        num_examples: number of examples to be used
                      (in case one wants to overfit small data)
    """

    def __init__(self, root_dir, year, default_boxes,
                 new_size, num_examples=-1, augmentation=None):
        super(VOCDataset, self).__init__()
        self.idx_to_name = [
            'aeroplane', 'bicycle', 'bird', 'boat',
            'bottle', 'bus', 'car', 'cat', 'chair',
            'cow', 'diningtable', 'dog', 'horse',
            'motorbike', 'person', 'pottedplant',
            'sheep', 'sofa', 'train', 'tvmonitor']
        self.name_to_idx = dict([(v, k)
                                 for k, v in enumerate(self.idx_to_name)])

        self.data_dir = os.path.join(root_dir, 'VOC{}'.format(year))
        self.image_dir = os.path.join(self.data_dir, 'JPEGImages')
        self.anno_dir = os.path.join(self.data_dir, 'Annotations')
        self.ids = list(map(lambda x: x[:-4], os.listdir(self.image_dir)))
        self.default_boxes = default_boxes
        self.new_size = new_size

        if num_examples != -1:
            self.ids = self.ids[:num_examples]

        self.train_ids = self.ids[:int(len(self.ids) * 0.75)]
        self.val_ids = self.ids[int(len(self.ids) * 0.75):]

        if augmentation == None:
            self.augmentation = ['original']
        else:
            self.augmentation = augmentation + ['original']

    def __len__(self):
        return len(self.ids)

    def _get_image(self, index):
        """ Method to read image from file
            then resize to (300, 300)
            then subtract by ImageNet's mean
            then convert to Tensor

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (3, 300, 300)
        """
        filename = self.ids[index]
        img_path = os.path.join(self.image_dir, filename + '.jpg')
        img = Image.open(img_path)

        return img

    def _get_annotation(self, index, orig_shape):
        """ Method to read annotation from file
            Boxes are normalized to image size
            Integer labels are increased by 1

        Args:
            index: the index to get filename from self.ids
            orig_shape: image's original shape

        Returns:
            boxes: numpy array of shape (num_gt, 4)
            labels: numpy array of shape (num_gt,)
        """
        h, w = orig_shape
        filename = self.ids[index]
        anno_path = os.path.join(self.anno_dir, filename + '.xml')
        objects = ET.parse(anno_path).findall('object')
        boxes = []
        labels = []

        for obj in objects:
            name = obj.find('name').text.lower().strip()
            bndbox = obj.find('bndbox')
            xmin = (float(bndbox.find('xmin').text) - 1) / w
            ymin = (float(bndbox.find('ymin').text) - 1) / h
            xmax = (float(bndbox.find('xmax').text) - 1) / w
            ymax = (float(bndbox.find('ymax').text) - 1) / h
            boxes.append([xmin, ymin, xmax, ymax])

            labels.append(self.name_to_idx[name] + 1)

        return np.array(boxes, dtype=np.float32), np.array(labels, dtype=np.int64)

    def generate(self, subset=None):
        """ The __getitem__ method
            so that the object can be iterable

        Args:
            index: the index to get filename from self.ids

        Returns:
            img: tensor of shape (300, 300, 3)
            boxes: tensor of shape (num_gt, 4)
            labels: tensor of shape (num_gt,)
        """
        if subset == 'train':
            indices = self.train_ids
        elif subset == 'val':
            indices = self.val_ids
        else:
            indices = self.ids
        for index in range(len(indices)):
            # img, orig_shape = self._get_image(index)
            filename = indices[index]
            img = self._get_image(index)
            w, h = img.size
            boxes, labels = self._get_annotation(index, (h, w))
            boxes = tf.constant(boxes, dtype=tf.float32)
            labels = tf.constant(labels, dtype=tf.int64)

            augmentation_method = np.random.choice(self.augmentation)
            if augmentation_method == 'patch':
                img, boxes, labels = random_patching(img, boxes, labels)
            elif augmentation_method == 'flip':
                img, boxes, labels = horizontal_flip(img, boxes, labels)

            img = np.array(img.resize(
                (self.new_size, self.new_size)), dtype=np.float32)
            img = (img / 127.0) - 1.0
            img = tf.constant(img, dtype=tf.float32)

            gt_confs, gt_locs = compute_target(
                self.default_boxes, boxes, labels)

            yield filename, img, gt_confs, gt_locs
            
            
def create_batch_generator_with_custom_findarea_set(root_dir,
                           new_size, batch_size, num_batches,
                           mode,
                           augmentation=None):
 
    num_examples = batch_size * num_batches if num_batches > 0 else -1
    print('num_examples = ' , num_examples)
    CuDset = Custom_find_area_Dataset(root_dir,
                     new_size, num_examples, augmentation)

    info = {
        'idx_to_name': CuDset.idx_to_name,
        'name_to_idx': CuDset.name_to_idx,
        'length': len(CuDset),
        'image_dir': CuDset.image_dir,
        'anno_dir': CuDset.anno_dir
    }

    if mode == 'train':
        train_gen = partial(CuDset.generate, subset='train')
        train_dataset = tf.data.Dataset.from_generator(
            train_gen, (tf.string, tf.float32, tf.int64, tf.float32))
        val_gen = partial(CuDset.generate, subset='val')
        val_dataset = tf.data.Dataset.from_generator(
            val_gen, (tf.string, tf.float32, tf.int64, tf.float32))

        train_dataset = train_dataset.shuffle(40).batch(batch_size)
        val_dataset = val_dataset.batch(batch_size)

        return train_dataset.take(num_batches), val_dataset.take(-1), info
    else:
        dataset = tf.data.Dataset.from_generator(
            CuDset.generate, (tf.string, tf.float32))
        dataset = dataset.batch(batch_size)
        return dataset.take(num_batches), info
    
def create_batch_generator_with_customset_area(root_dir, default_boxes,
                           new_size, batch_size, num_batches,
                           mode,
                           augmentation=None):
    num_examples = batch_size * num_batches if num_batches > 0 else -1
    
    if mode == 'test':
        CuDset = CustomDataset_for_test(root_dir, default_boxes,
                     new_size, num_examples, augmentation)
        info = {
            'idx_to_name': CuDset.idx_to_name,
            'name_to_idx': CuDset.name_to_idx,
            'length': len(CuDset),
            'image_dir': CuDset.image_dir,
        }

    else : 
        CuDset = CustomDataset_area(root_dir, default_boxes,
                     new_size, num_examples, augmentation)
        info = {
            'idx_to_name': CuDset.idx_to_name,
            'name_to_idx': CuDset.name_to_idx,
            'length': len(CuDset),
            'image_dir': CuDset.image_dir,
            'anno_dir': CuDset.anno_dir
        }
        

    if mode == 'train':
        train_gen = partial(CuDset.generate, subset='train')
        train_dataset = tf.data.Dataset.from_generator(
            train_gen, (tf.string, tf.float32, tf.int64, tf.float32))
        val_gen = partial(CuDset.generate, subset='val')
        val_dataset = tf.data.Dataset.from_generator(
            val_gen, (tf.string, tf.float32, tf.int64, tf.float32))

        train_dataset = train_dataset.shuffle(40).batch(batch_size)
        val_dataset = val_dataset.batch(batch_size)

        return train_dataset.take(num_batches), val_dataset.take(-1), info
    else:
        dataset = tf.data.Dataset.from_generator(
            CuDset.generate, (tf.string, tf.float32))
        dataset = dataset.batch(batch_size)
        return dataset.take(num_batches), info
            
            
def create_batch_generator_with_customset(root_dir, default_boxes,
                           new_size, batch_size, num_batches,
                           mode,
                           augmentation=None):
    num_examples = batch_size * num_batches if num_batches > 0 else -1
    
    if mode == 'test':
        CuDset = CustomDataset_for_test(root_dir, default_boxes,
                     new_size, num_examples, augmentation)
        info = {
            'idx_to_name': CuDset.idx_to_name,
            'name_to_idx': CuDset.name_to_idx,
            'length': len(CuDset),
            'image_dir': CuDset.image_dir,
        }

    else : 
        CuDset = CustomDataset(root_dir, default_boxes,
                     new_size, num_examples, augmentation)
        info = {
            'idx_to_name': CuDset.idx_to_name,
            'name_to_idx': CuDset.name_to_idx,
            'length': len(CuDset),
            'image_dir': CuDset.image_dir,
            'anno_dir': CuDset.anno_dir
        }
        

    if mode == 'train':
        train_gen = partial(CuDset.generate, subset='train')
        train_dataset = tf.data.Dataset.from_generator(
            train_gen, (tf.string, tf.float32, tf.int64, tf.float32))
        val_gen = partial(CuDset.generate, subset='val')
        val_dataset = tf.data.Dataset.from_generator(
            val_gen, (tf.string, tf.float32, tf.int64, tf.float32))

        train_dataset = train_dataset.shuffle(40).batch(batch_size)
        val_dataset = val_dataset.batch(batch_size)

        return train_dataset.take(num_batches), val_dataset.take(-1), info
    else:
        dataset = tf.data.Dataset.from_generator(
            CuDset.generate, (tf.string, tf.float32))
        dataset = dataset.batch(batch_size)
        return dataset.take(num_batches), info



def create_batch_generator(root_dir, year, default_boxes,
                           new_size, batch_size, num_batches,
                           mode,
                           augmentation=None):
    num_examples = batch_size * num_batches if num_batches > 0 else -1
    voc = VOCDataset(root_dir, year, default_boxes,
                     new_size, num_examples, augmentation)

    info = {
        'idx_to_name': voc.idx_to_name,
        'name_to_idx': voc.name_to_idx,
        'length': len(voc),
        'image_dir': voc.image_dir,
        'anno_dir': voc.anno_dir
    }

    if mode == 'train':
        train_gen = partial(voc.generate, subset='train')
        train_dataset = tf.data.Dataset.from_generator(
            train_gen, (tf.string, tf.float32, tf.int64, tf.float32))
        val_gen = partial(voc.generate, subset='val')
        val_dataset = tf.data.Dataset.from_generator(
            val_gen, (tf.string, tf.float32, tf.int64, tf.float32))

        train_dataset = train_dataset.shuffle(40).batch(batch_size)
        val_dataset = val_dataset.batch(batch_size)

        return train_dataset.take(num_batches), val_dataset.take(-1), info
    else:
        dataset = tf.data.Dataset.from_generator(
            voc.generate, (tf.string, tf.float32, tf.int64, tf.float32))
        dataset = dataset.batch(batch_size)
        return dataset.take(num_batches), info
