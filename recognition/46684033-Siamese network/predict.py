#predict.py
import torch
import dataset
import torch.nn.functional as F
import torchvision
import torchvision.transforms as transforms
import random
import dataset
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
if not torch.cuda.is_available():
    print("Warning VUDA not Found. Using CPU")

train_path = r"C:/Users/wongm/Downloads/ADNI_AD_NC_2D/AD_NC/train"
test_path = r"C:/Users/wongm/Downloads/ADNI_AD_NC_2D/AD_NC/test"

model = torch.load(r"C:/Users/wongm/Desktop/COMP3710/project/siamese_epcoh30.pth")
model.eval()



transform = transforms.Compose([
    # transforms.Resize((128, 128)),
    transforms.ToTensor(),

])
train_path = r"C:/Users/wongm/Downloads/ADNI_AD_NC_2D/AD_NC/train"
test_path = r"C:/Users/wongm/Downloads/ADNI_AD_NC_2D/AD_NC/test"
trainset = torchvision.datasets.ImageFolder(root=train_path, transform=transform)
testset = torchvision.datasets.ImageFolder(root=test_path, transform=transform)
paired_testset = dataset.SiameseDatset_test(trainset,testset)
train_loader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(paired_testset, batch_size=64,shuffle=True)
correct = 0
total = 0

with torch.no_grad():
    for i, (test_images,pos_image1,pos_image2,pos_image3, neg_image1,neg_image2,neg_image3,test_labels) in enumerate(test_loader):
        test_images = test_images.to(device)
        pos_image1 = pos_image1.to(device)
        neg_image1 = neg_image1.to(device)
        pos_image2 = pos_image2.to(device)
        neg_image2 = neg_image2.to(device)
        pos_image3 = pos_image3.to(device)
        neg_image3 = neg_image3.to(device)
        test_labels = test_labels.to(device)


        x1, y1 = model(test_images,pos_image1)
        x2, y2 = model(test_images, pos_image2)
        x3, y3 = model(test_images, pos_image3)
        # accuracy test
        pos_distances1 = (y1 - x1).pow(2).sum(1)
        pos_distances2 = (y2 - x2).pow(2).sum(1)
        pos_distances3 = (y3 - x3).pow(2).sum(1)
        mean_pos_distances = (pos_distances1 + pos_distances2 + pos_distances3) / 3
        x4, y4 = model(test_images,neg_image1)
        x5, y5 = model(test_images, neg_image2)
        x6, y6 = model(test_images, neg_image3)
        neg_distances1 = (y4 - x4).pow(2).sum(1)
        neg_distances2 = (y5 - x5).pow(2).sum(1)
        neg_distances3 = (y6 - x6).pow(2).sum(1)
        mean_neg_distances = (neg_distances1 + neg_distances2 + neg_distances3) / 3
        pred = torch.where(mean_pos_distances < mean_neg_distances, 1, 0)

        correct += (pred == 1).sum().item()
        total += test_labels.size(0)
        print(f"progress [{i}/{len(test_loader)}]")
        print(f"test accuracy {100*correct/total}%")

    #TODO
    # test all model in certain epoch
    # include average result