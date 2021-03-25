import os

import cv2
import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset
import random

import cv2
import random
import glob

class DS_inpaint(Dataset):
    def __init__(self, root, transform=None, size=256):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform
        self.mask_dir = '/content/masks'
        self.files = glob.glob(self.mask_dir + '/**/*.png', recursive=True)
        files_jpg = glob.glob(self.mask_dir + '/**/*.jpg', recursive=True)
        self.files.extend(files_jpg)

        self.size = size

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        sample = Image.open(sample_path).convert('RGB')

        if self.transform:
            sample = self.transform(sample)

        # if edges are required
        grayscale = cv2.cvtColor(np.array(sample), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(grayscale,100,150)
        grayscale = torch.from_numpy(grayscale).unsqueeze(0)/255
        edges = torch.from_numpy(edges).unsqueeze(0)

        if random.uniform(0, 1) < 0.5:
          # generating mask automatically with 50% chance
          mask = DS.random_mask(height=self.size, width=self.size)
          mask = torch.from_numpy(mask)

        else:
          # load random mask from folder
          mask = cv2.imread(random.choice([x for x in self.files]), cv2.IMREAD_UNCHANGED)
          mask = cv2.resize(mask, (self.size,self.size), interpolation=cv2.INTER_NEAREST)

          # flip mask randomly
          if 0.3 < random.uniform(0, 1) <= 0.66:
            mask = np.flip(mask, axis=0)
          elif 0.66 < random.uniform(0, 1) <= 1:
            mask = np.flip(mask, axis=1)

          mask = torch.from_numpy(mask.astype(np.float32)).unsqueeze(0)/255

        #sample = torch.from_numpy(sample)
        sample = transforms.ToTensor()(sample)

        # apply mask
        masked = sample * mask
        return masked, mask, sample

        # EdgeConnect
        #return masked, mask, sample, edges, grayscale

        # PRVS
        #return masked, mask, sample, edges


    @staticmethod
    def random_mask(height=256, width=256,
                    min_stroke=1, max_stroke=4,
                    min_vertex=1, max_vertex=12,
                    min_brush_width_divisor=16, max_brush_width_divisor=10):
        mask = np.ones((height, width))

        min_brush_width = height // min_brush_width_divisor
        max_brush_width = height // max_brush_width_divisor
        max_angle = 2*np.pi
        num_stroke = np.random.randint(min_stroke, max_stroke+1)
        average_length = np.sqrt(height*height + width*width) / 8

        for _ in range(num_stroke):
            num_vertex = np.random.randint(min_vertex, max_vertex+1)
            start_x = np.random.randint(width)
            start_y = np.random.randint(height)

            for _ in range(num_vertex):
                angle = np.random.uniform(max_angle)
                length = np.clip(np.random.normal(average_length, average_length//2), 0, 2*average_length)
                brush_width = np.random.randint(min_brush_width, max_brush_width+1)
                end_x = (start_x + length * np.sin(angle)).astype(np.int32)
                end_y = (start_y + length * np.cos(angle)).astype(np.int32)

                cv2.line(mask, (start_y, start_x), (end_y, end_x), 0., brush_width)

                start_x, start_y = end_x, end_y
        if np.random.random() < 0.5:
            mask = np.fliplr(mask)
        if np.random.random() < 0.5:
            mask = np.flipud(mask)
        return mask.reshape((1,)+mask.shape).astype(np.float32)



class DS_inpaint_val(Dataset):
    def __init__(self, root, transform=None):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        #sample = Image.open(sample_path).convert('RGB')
        sample = cv2.imread(sample_path)
        sample = cv2.cvtColor(sample, cv2.COLOR_BGR2RGB)

        # if edges are required
        grayscale = cv2.cvtColor(sample, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(grayscale,100,150)
        grayscale = torch.from_numpy(grayscale).unsqueeze(0)
        edges = torch.from_numpy(edges).unsqueeze(0)

        green_mask = 1-np.all(sample == [0,255,0], axis=-1).astype(int)
        green_mask = torch.from_numpy(green_mask).unsqueeze(0)
        sample = torch.from_numpy(sample.astype(np.float32)).permute(2, 0, 1)/255
        sample = sample * green_mask

        # train_batch[0] = masked
        # train_batch[1] = mask
        # train_batch[2] = path
        return sample, green_mask, sample_path

        # EdgeConnect
        #return sample, green_mask, sample_path, edges, grayscale

        # PRVS
        #return sample, green_mask, sample_path, edges
















class DS_inpaint_tiled(Dataset):
    def __init__(self, root, transform=None, size=256):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform
        self.mask_dir = '/content/masks'
        self.files = glob.glob(self.mask_dir + '/**/*.png', recursive=True)
        files_jpg = glob.glob(self.mask_dir + '/**/*.jpg', recursive=True)
        self.files.extend(files_jpg)

        self.size = size

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        #sample = Image.open(sample_path).convert('RGB')
        sample = cv2.imread(sample_path)


        x_rand = random.randint(0,15)
        y_rand = random.randint(0,15)

        sample = sample[x_rand*256:(x_rand+1)*256, y_rand*256:(y_rand+1)*256]
        sample = cv2.cvtColor(sample, cv2.COLOR_BGR2RGB)

        #sample = torch.from_numpy(sample)

        #if self.transform:
        #    sample = self.transform(sample)

        # if edges are required
        grayscale = cv2.cvtColor(np.array(sample), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(grayscale,100,150)
        grayscale = torch.from_numpy(grayscale).unsqueeze(0)/255
        edges = torch.from_numpy(edges).unsqueeze(0)

        if random.uniform(0, 1) < 0.5:
          # generating mask automatically with 50% chance
          mask = DS.random_mask(height=self.size, width=self.size)
          mask = torch.from_numpy(mask)

        else:
          # load random mask from folder
          mask = cv2.imread(random.choice([x for x in self.files]), cv2.IMREAD_UNCHANGED)
          mask = cv2.resize(mask, (self.size,self.size), interpolation=cv2.INTER_NEAREST)

          # flip mask randomly
          if 0.3 < random.uniform(0, 1) <= 0.66:
            mask = np.flip(mask, axis=0)
          elif 0.66 < random.uniform(0, 1) <= 1:
            mask = np.flip(mask, axis=1)

          mask = torch.from_numpy(mask.astype(np.float32)).unsqueeze(0)/255

        sample = torch.from_numpy(sample).permute(2, 0, 1)/255
        #sample = transforms.ToTensor()(sample)

        # apply mask
        #print(sample.shape)
        #print(mask.shape)
        masked = sample * mask
        return masked, mask, sample

        # EdgeConnect
        #return masked, mask, sample, edges, grayscale

        # PRVS
        #return masked, mask, sample, edges


    @staticmethod
    def random_mask(height=256, width=256,
                    min_stroke=1, max_stroke=4,
                    min_vertex=1, max_vertex=12,
                    min_brush_width_divisor=16, max_brush_width_divisor=10):
        mask = np.ones((height, width))

        min_brush_width = height // min_brush_width_divisor
        max_brush_width = height // max_brush_width_divisor
        max_angle = 2*np.pi
        num_stroke = np.random.randint(min_stroke, max_stroke+1)
        average_length = np.sqrt(height*height + width*width) / 8

        for _ in range(num_stroke):
            num_vertex = np.random.randint(min_vertex, max_vertex+1)
            start_x = np.random.randint(width)
            start_y = np.random.randint(height)

            for _ in range(num_vertex):
                angle = np.random.uniform(max_angle)
                length = np.clip(np.random.normal(average_length, average_length//2), 0, 2*average_length)
                brush_width = np.random.randint(min_brush_width, max_brush_width+1)
                end_x = (start_x + length * np.sin(angle)).astype(np.int32)
                end_y = (start_y + length * np.cos(angle)).astype(np.int32)

                cv2.line(mask, (start_y, start_x), (end_y, end_x), 0., brush_width)

                start_x, start_y = end_x, end_y
        if np.random.random() < 0.5:
            mask = np.fliplr(mask)
        if np.random.random() < 0.5:
            mask = np.flipud(mask)
        return mask.reshape((1,)+mask.shape).astype(np.float32)



class DS_inpaint_tiled_val(Dataset):
    def __init__(self, root, transform=None):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        #sample = Image.open(sample_path).convert('RGB')
        sample = cv2.imread(sample_path)
        sample = cv2.cvtColor(sample, cv2.COLOR_BGR2RGB)

        # if edges are required
        grayscale = cv2.cvtColor(sample, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(grayscale,100,150)
        grayscale = torch.from_numpy(grayscale).unsqueeze(0)
        edges = torch.from_numpy(edges).unsqueeze(0)

        green_mask = 1-np.all(sample == [0,255,0], axis=-1).astype(int)
        green_mask = torch.from_numpy(green_mask).unsqueeze(0)
        sample = torch.from_numpy(sample.astype(np.float32)).permute(2, 0, 1)/255
        sample = sample * green_mask

        # train_batch[0] = masked
        # train_batch[1] = mask
        # train_batch[2] = path
        return sample, green_mask, sample_path

        # EdgeConnect
        #return sample, green_mask, sample_path, edges, grayscale

        # PRVS
        #return sample, green_mask, sample_path, edges














class DS_inpaint_tiled_batch(Dataset):
    def __init__(self, root, transform=None, size=256, batch_size_DL = 3):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform
        self.mask_dir = '/content/masks'
        self.files = glob.glob(self.mask_dir + '/**/*.png', recursive=True)
        files_jpg = glob.glob(self.mask_dir + '/**/*.jpg', recursive=True)
        self.files.extend(files_jpg)

        self.size = size
        self.batch_size = batch_size_DL

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        sample = cv2.imread(sample_path)

        #batch_size = 10
        pos_total = []
        self.total_size = 0

        while True:
          # determine random position
          x_rand = random.randint(0,15)
          y_rand = random.randint(0,15)

          pos_rand = [x_rand, y_rand]

          if (pos_rand in pos_total) != True:
            pos_total.append(pos_rand)
            self.total_size += 1

          # return batchsize
          if self.total_size == self.batch_size:
            break

        self.total_size = 0
        for i in pos_total:
          # creating sample if for start
          """
          print("pos_total")
          print(pos_total)

          print("i")
          print(i)
          """
          if self.total_size == 0:
            sample_add = sample[i[0]*256:(i[0]+1)*256, i[1]*256:(i[1]+1)*256]
            sample_add = cv2.cvtColor(sample_add, cv2.COLOR_BGR2RGB)
            sample_add = torch.from_numpy(sample_add).permute(2, 0, 1).unsqueeze(0)/255

            # if edges are required
            """
            grayscale = cv2.cvtColor(np.array(sample_add), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(grayscale,100,150)
            grayscale = torch.from_numpy(grayscale).unsqueeze(0)/255
            edges = torch.from_numpy(edges).unsqueeze(0)
            """

            self.total_size += 1
          else:
            sample_add2 = sample[i[0]*256:(i[0]+1)*256, i[1]*256:(i[1]+1)*256]
            sample_add2 = cv2.cvtColor(sample_add2, cv2.COLOR_BGR2RGB)
            # if edges are required
            """
            grayscale = cv2.cvtColor(np.array(sample_add2), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(grayscale,100,150)
            grayscale = torch.from_numpy(grayscale).unsqueeze(0)/255
            edges = torch.from_numpy(edges).unsqueeze(0)
            """
            sample_add2 = torch.from_numpy(sample_add2).permute(2, 0, 1).unsqueeze(0)/255
            sample_add = torch.cat((sample_add, sample_add2), dim=0)

        # getting mask batch

        self.total_size = 0
        for i in range(self.batch_size):
          # randommly loading one mask

          if random.uniform(0, 1) < 0.5:
            # generating mask automatically with 50% chance
            mask = DS.random_mask(height=self.size, width=self.size)
            mask = torch.from_numpy(mask.astype(np.float32)).unsqueeze(0)
            #print("random mask")
            #print(mask.shape)

          else:
            # load random mask from folder
            mask = cv2.imread(random.choice([x for x in self.files]), cv2.IMREAD_UNCHANGED)
            mask = cv2.resize(mask, (self.size,self.size), interpolation=cv2.INTER_NEAREST)

            # flip mask randomly
            if 0.3 < random.uniform(0, 1) <= 0.66:
              mask = np.flip(mask, axis=0)
            elif 0.66 < random.uniform(0, 1) <= 1:
              mask = np.flip(mask, axis=1)
            mask = torch.from_numpy(mask.astype(np.float32)).unsqueeze(0).unsqueeze(0)
            #print("read mask")
            #print(mask.shape)

          if self.total_size == 0:
            mask_add = mask/255
            self.total_size += 1
          else:
            mask_add2 = mask/255
            mask_add = torch.cat((mask_add, mask_add2), dim=0)
            self.total_size += 1

        # apply mask
        masked = sample_add * mask_add

        return masked, mask_add, sample_add

        # EdgeConnect
        #return masked, mask, sample, edges, grayscale

        # PRVS
        #return masked, mask, sample, edges


    @staticmethod
    def random_mask(height=256, width=256,
                    min_stroke=1, max_stroke=4,
                    min_vertex=1, max_vertex=12,
                    min_brush_width_divisor=16, max_brush_width_divisor=10):
        mask = np.ones((height, width))

        min_brush_width = height // min_brush_width_divisor
        max_brush_width = height // max_brush_width_divisor
        max_angle = 2*np.pi
        num_stroke = np.random.randint(min_stroke, max_stroke+1)
        average_length = np.sqrt(height*height + width*width) / 8

        for _ in range(num_stroke):
            num_vertex = np.random.randint(min_vertex, max_vertex+1)
            start_x = np.random.randint(width)
            start_y = np.random.randint(height)

            for _ in range(num_vertex):
                angle = np.random.uniform(max_angle)
                length = np.clip(np.random.normal(average_length, average_length//2), 0, 2*average_length)
                brush_width = np.random.randint(min_brush_width, max_brush_width+1)
                end_x = (start_x + length * np.sin(angle)).astype(np.int32)
                end_y = (start_y + length * np.cos(angle)).astype(np.int32)

                cv2.line(mask, (start_y, start_x), (end_y, end_x), 0., brush_width)

                start_x, start_y = end_x, end_y
        if np.random.random() < 0.5:
            mask = np.fliplr(mask)
        if np.random.random() < 0.5:
            mask = np.flipud(mask)
        return mask.reshape((1,)+mask.shape).astype(np.float32)



class DS_inpaint_tiled_batch_val(Dataset):
    def __init__(self, root, transform=None):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        #sample = Image.open(sample_path).convert('RGB')
        sample = cv2.imread(sample_path)
        sample = cv2.cvtColor(sample, cv2.COLOR_BGR2RGB)

        # if edges are required
        grayscale = cv2.cvtColor(sample, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(grayscale,100,150)
        grayscale = torch.from_numpy(grayscale).unsqueeze(0)
        edges = torch.from_numpy(edges).unsqueeze(0)

        green_mask = 1-np.all(sample == [0,255,0], axis=-1).astype(int)
        green_mask = torch.from_numpy(green_mask).unsqueeze(0)
        sample = torch.from_numpy(sample.astype(np.float32)).permute(2, 0, 1)/255
        sample = sample * green_mask

        # train_batch[0] = masked
        # train_batch[1] = mask
        # train_batch[2] = path
        return sample, green_mask, sample_path

        # EdgeConnect
        #return sample, green_mask, sample_path, edges, grayscale

        # PRVS
        #return sample, green_mask, sample_path, edges









class DS_lrhr(Dataset):
    def __init__(self, lr_path, hr_path, hr_size, scale):
        self.samples = []
        for hr_path, _, fnames in sorted(os.walk(hr_path)):
            for fname in sorted(fnames):
                path = os.path.join(hr_path, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + hr_path)
        self.hr_size = hr_size
        self.scale = scale
        self.lr_path = lr_path

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        # getting hr image
        hr_path = self.samples[index]
        hr_image = cv2.imread(hr_path)
        hr_image = cv2.cvtColor(hr_image, cv2.COLOR_BGR2RGB)

        # getting lr image
        lr_path = os.path.join(self.lr_path, os.path.basename(hr_path))
        lr_image = cv2.imread(lr_path)
        lr_image = cv2.cvtColor(lr_image, cv2.COLOR_BGR2RGB)

        # checking for hr_size limitation
        if hr_image.shape[0] > self.hr_size or hr_image.shape[1] > self.hr_size:
          # image too big, random crop
          random_pos1 = random.randint(0,hr_image.shape[0]-self.hr_size)
          random_pos2 = random.randint(0,hr_image.shape[0]-self.hr_size)

          image_hr = hr_image[random_pos1:random_pos1+self.hr_size, random_pos2:random_pos2+self.hr_size]
          image_lr = lr_image[int(random_pos1/self.scale):int((random_pos2+self.hr_size)/self.scale), int(random_pos2/self.scale):int((random_pos2+self.hr_size)/self.scale)]

        # to tensor
        hr_image = torch.from_numpy(hr_image).permute(2, 0, 1)/255
        lr_image = torch.from_numpy(lr_image).permute(2, 0, 1)/255

        return 0, lr_image, hr_image


class DS_lrhr_val(Dataset):
    def __init__(self, lr_path, hr_path):
        self.samples = []
        for hr_path, _, fnames in sorted(os.walk(hr_path)):
            for fname in sorted(fnames):
                path = os.path.join(hr_path, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + hr_path)

        self.lr_path = lr_path

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        # getting hr image
        hr_path = self.samples[index]
        hr_image = cv2.imread(hr_path)

        # getting lr image
        lr_path = os.path.join(self.lr_path, os.path.basename(hr_path))
        lr_image = cv2.imread(lr_path)

        # to tensor
        hr_image = torch.from_numpy(hr_image).permute(2, 0, 1)/255
        lr_image = torch.from_numpy(lr_image).permute(2, 0, 1)/255

        return lr_image, hr_image, lr_path














class DS_lrhr_batch_oft(Dataset):
    def __init__(self, root, transform=None, size=256, batch_size_DL = 3, scale=4, image_size=400, amount_tiles=3):
        self.samples = []
        for root, _, fnames in sorted(os.walk(root)):
            for fname in sorted(fnames):
                path = os.path.join(root, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + root)

        self.transform = transform

        #self.size = size
        self.image_size = image_size # how big one tile is
        self.scale = scale
        self.batch_size = batch_size_DL
        self.interpolation_method = [cv2.INTER_NEAREST, cv2.INTER_LINEAR, cv2.INTER_AREA, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4]
        self.amount_tiles = amount_tiles

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        sample_path = self.samples[index]
        sample = cv2.imread(sample_path, cv2.IMREAD_GRAYSCALE)


        pos_total = []

        self.total_size = 0 # the current amount of images that got a random position

        while True:
          # determine random position
          x_rand = random.randint(0,self.amount_tiles-1)
          y_rand = random.randint(0,self.amount_tiles-1)

          pos_rand = [x_rand, y_rand]

          if (pos_rand in pos_total) != True:
            pos_total.append(pos_rand)
            self.total_size += 1

          # return batchsize
          if self.total_size == self.batch_size:
            break

        self.total_size = 0 # counter for making sure array gets appended if processed images > 1

        for i in pos_total:
          # creating sample if for start
          if self.total_size == 0:
            # cropping from hr image
            image_hr = sample[i[0]*self.image_size:(i[0]+1)*self.image_size, i[1]*self.image_size:(i[1]+1)*self.image_size]
            # creating lr on the fly
            #image_lr = cv2.resize(image_hr, (int(self.image_size/self.scale), int(self.image_size/self.scale)), interpolation=random.choice(self.interpolation_method))
            image_lr = cv2.resize(image_hr, (int(self.image_size/self.scale), int(self.image_size/self.scale)), interpolation=random.choice(self.interpolation_method))

            """
            print("-----------------------")
            print(i[0]*(self.image_size/self.scale))
            print((i[0]+1)*(self.image_size/self.scale))

            print(i[1]*(self.image_size/self.scale))
            print((i[1]+1)*(self.image_size/self.scale))
            """
            #image_lr = image_lr[i[0]*(self.image_size/self.scale):(i[0]+1)*(self.image_size/self.scale), i[1]*(self.image_size/self.scale):(i[1]+1)*(self.image_size/self.scale)]


            # creating torch tensor
            image_hr = torch.from_numpy(image_hr).unsqueeze(2).permute(2, 0, 1).unsqueeze(0)/255
            image_lr = torch.from_numpy(image_lr).unsqueeze(2).permute(2, 0, 1).unsqueeze(0)/255


            # if edges are required
            """
            grayscale = cv2.cvtColor(np.array(sample_add), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(grayscale,100,150)
            grayscale = torch.from_numpy(grayscale).unsqueeze(0)/255
            edges = torch.from_numpy(edges).unsqueeze(0)
            """

            self.total_size += 1
          else:
            # cropping from hr image
            image_hr2 = sample[i[0]*self.image_size:(i[0]+1)*self.image_size, i[1]*self.image_size:(i[1]+1)*self.image_size]
            # creating lr on the fly
            #image_lr2 = cv2.resize(image_hr2, (int(self.image_size/self.scale), int(self.image_size/self.scale)), interpolation=random.choice(self.interpolation_method))
            #image_lr2 = image_lr2[i[0]*(self.image_size/self.scale):(i[0]+1)*(self.image_size/self.scale), i[1]*(self.image_size/self.scale):(i[1]+1)*(self.image_size/self.scale)]
            image_lr2 = cv2.resize(image_hr2, (int(self.image_size/self.scale), int(self.image_size/self.scale)), interpolation=random.choice(self.interpolation_method))



            # if edges are required
            """
            grayscale = cv2.cvtColor(np.array(sample_add2), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(grayscale,100,150)
            grayscale = torch.from_numpy(grayscale).unsqueeze(0)/255
            edges = torch.from_numpy(edges).unsqueeze(0)
            """
            # creating torch tensor
            image_hr2 = torch.from_numpy(image_hr2).unsqueeze(2).permute(2, 0, 1).unsqueeze(0)/255
            image_hr = torch.cat((image_hr, image_hr2), dim=0)

            image_lr2 = torch.from_numpy(image_lr2).unsqueeze(2).permute(2, 0, 1).unsqueeze(0)/255
            image_lr = torch.cat((image_lr, image_lr2), dim=0)

        return 0, image_lr, image_hr


class DS_lrhr_batch_oft_val(Dataset):
    def __init__(self, lr_path, hr_path):
        self.samples = []
        for hr_path, _, fnames in sorted(os.walk(hr_path)):
            for fname in sorted(fnames):
                path = os.path.join(hr_path, fname)
                self.samples.append(path)
        if len(self.samples) == 0:
            raise RuntimeError("Found 0 files in subfolders of: " + hr_path)

        self.lr_path = lr_path

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        # getting hr image
        hr_path = self.samples[index]
        hr_image = cv2.imread(hr_path, cv2.IMREAD_GRAYSCALE)

        # getting lr image
        lr_path = os.path.join(self.lr_path, os.path.basename(hr_path))
        lr_image = cv2.imread(lr_path, cv2.IMREAD_GRAYSCALE)



        hr_image = torch.from_numpy(hr_image).unsqueeze(2).permute(2, 0, 1).unsqueeze(0)/255
        lr_image = torch.from_numpy(lr_image).unsqueeze(2).permute(2, 0, 1).unsqueeze(0)/255


        return lr_image, hr_image, lr_path
