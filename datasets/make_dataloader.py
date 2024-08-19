import os
from torchvision import transforms, datasets
from datasets.Dataloader_University import Sampler_University,Dataloader_University,train_collate_fn
from .random_erasing import RandomErasing
from .autoaugment import ImageNetPolicy, CIFAR10Policy
import torch

def make_dataset(opt):
    ######################################################################
    # Load Data
    # ---------
    #

    transform_train_list = [
        # transforms.RandomResizedCrop(size=(opt.h, opt.w), scale=(0.75,1.0), ratio=(0.75,1.3333), interpolation=3), #Image.BICUBIC)
        transforms.Resize((opt.h, opt.w), interpolation=3),
        transforms.Pad(opt.pad, padding_mode='edge'),
        transforms.RandomCrop((opt.h, opt.w)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]

    transform_satellite_list = [
        transforms.Resize((opt.h, opt.w), interpolation=3),
        transforms.Pad(opt.pad, padding_mode='edge'),
        transforms.RandomAffine(90),
        transforms.RandomCrop((opt.h, opt.w)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]

    transform_val_list = [
        transforms.Resize(size=(opt.h, opt.w), interpolation=3),  # Image.BICUBIC
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]

    if opt.erasing_p > 0:
        transform_train_list = transform_train_list + [RandomErasing(probability=opt.erasing_p, mean=[0.0, 0.0, 0.0])]

    if opt.color_jitter:
        transform_train_list = [transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1,
                                                       hue=0)] + transform_train_list
        transform_satellite_list = [transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1,
                                                           hue=0)] + transform_satellite_list

    if opt.DA:
        transform_train_list = [ImageNetPolicy()] + transform_train_list

    print(transform_train_list)
    data_transforms = {
        'train': transforms.Compose(transform_train_list),
        'val': transforms.Compose(transform_val_list),
        'satellite': transforms.Compose(transform_satellite_list)}

    train_all = ''
    if opt.train_all:
        train_all = '_all'

    data_dir = "/home/disk/reid-survey/codes/RK-Net-main/data/building/train"

    image_datasets = {
        'sat': datasets.ImageFolder(os.path.join(data_dir, 'sat'), data_transforms['sat']),
        'side': datasets.ImageFolder(os.path.join(data_dir, 'side'), data_transforms['train'])
    }
    
    dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=opt.batchsize,
                                                shuffle=True, num_workers=2, pin_memory=True)
                for x in ['sat', 'side']}
    dataset_sizes = {x: len(image_datasets[x]) for x in ['sat', 'side']}
    class_names = image_datasets['side'].classes  # assuming the classes are the same in both folders
    print(dataset_sizes)
    return dataloaders,class_names,dataset_sizes

    # custom Dataset


    # image_datasets = Dataloader_University(opt.data_dir,transforms=data_transforms)
    # samper = Sampler_University(image_datasets,batchsize=opt.batchsize,sample_num=opt.sample_num)
    # dataloaders =torch.utils.data.DataLoader(image_datasets, batch_size=opt.batchsize,sampler=samper,num_workers=opt.num_worker, pin_memory=True,collate_fn=train_collate_fn)
    # dataset_sizes = {x: len(image_datasets)*opt.sample_num for x in ['satellite', 'drone']}
    # class_names = image_datasets.cls_names
    return dataloaders,class_names,dataset_sizes

