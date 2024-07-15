import cv2
import torch
import numpy as np
from ultralytics import YOLO
from classifier import SimpleCNN
from grad_cam import GradCam
import time
from torchvision import datasets, transforms
from PIL import Image

def visualize_cam_on_image(heatmap, original_image, alpha=0.5):
    # Assuming original_image is a NumPy array of shape (H, W, C)
    
    # Normalize the heatmap
    original_image = np.array(original_image, dtype=np.float32)
    heatmap_normalized = (heatmap - np.min(heatmap)) / (np.max(heatmap) - np.min(heatmap))

    # Resize heatmap to match the size of the original image
    heatmap_resized = cv2.resize(heatmap_normalized, (original_image.shape[1], original_image.shape[0]))

    # Apply a colormap (you can choose different colormaps)
    heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)

    # Overlay the heatmap on original image
    heatmap_colored = np.array(heatmap_colored, dtype=np.uint8)

    original_image = np.array(original_image * 255, dtype=np.uint8)
    superimposed_image = cv2.addWeighted(heatmap_colored, alpha, original_image, 1 - alpha, 0)

    # Display the image
    return superimposed_image

def predict(chosen_model, img, classes=[], conf=0.5):
    if classes:
        results = chosen_model.predict(img, classes=classes, conf=conf, verbose=False)
    else:
        results = chosen_model.predict(img, conf=conf, verbose=False)

    return results

def predict_and_detect(chosen_model, img, classes=None, conf=0.5, rectangle_thickness=2, text_thickness=1):
    results = predict(chosen_model, img, classes, conf=conf)
    box_sizes = []
    unique_names = set()
    for result in results:
        for box in result.boxes:
            x1, y1 = int(box.xyxy[0][0]), int(box.xyxy[0][1])
            x2, y2 = int(box.xyxy[0][2]), int(box.xyxy[0][3])
            area = (x2 - x1) * (y2 - y1)
            box_sizes.append(area)
            cv2.rectangle(img, (int(box.xyxy[0][0]), int(box.xyxy[0][1])),
                          (int(box.xyxy[0][2]), int(box.xyxy[0][3])), (255, 0, 0), rectangle_thickness)
            
            name = result.names[int(box.cls[0])]
            unique_names.add(name)

            cv2.putText(img, f"{result.names[int(box.cls[0])]}",
                        (int(box.xyxy[0][0]), int(box.xyxy[0][1]) - 10),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), text_thickness)
    return img, results, sum(box_sizes), unique_names

def analyse_and_classify_yolo(yolo_model, classifier_yolo, original_img):
    results = predict(yolo_model, original_img)
    images = []
    for result in results:
        for i, box in enumerate(result.boxes):
            crop = original_img[int(box.xyxy[0][1]):int(box.xyxy[0][3]), int(box.xyxy[0][0]):int(box.xyxy[0][2])]
            crop = cv2.resize(crop, (256, 256))
            # Store crop image
            timestamp = time.time()
            path = f'daten/unlabeled/{timestamp}_{i}.jpg'
            cv2.imwrite(path, crop)
            img, img_class, box_size, unique_names = predict_and_detect(classifier_yolo, crop)
            names = ' ,'.join(unique_names)
            img = Image.fromarray(np.array(img, dtype=np.uint8))
            images.append((img, names, box_size))
    return images

def analyse_and_classify(yolo_model, grad_cam, transform, original_img):
    results = predict(yolo_model, original_img)
    images = []
    for result in results:
        for i, box in enumerate(result.boxes):
            crop = original_img[int(box.xyxy[0][1]):int(box.xyxy[0][3]), int(box.xyxy[0][0]):int(box.xyxy[0][2])]
            crop = cv2.resize(crop, (256, 256))
            # Store crop image
            timestamp = time.time()
            path = f'daten/unlabeled/{timestamp}_{i}.jpg'
            cv2.imwrite(path, crop)
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
            crop = torch.from_numpy(crop).permute(2, 0, 1).unsqueeze(0).float().to('cuda')
            heatmap, target_class = grad_cam(crop)
            heatmap = heatmap.cpu().detach().numpy()[0]
            superimposed_image = visualize_cam_on_image(heatmap, crop.cpu().detach().numpy()[0].transpose(1, 2, 0))
            heatmap = Image.fromarray(superimposed_image)
            images.append((heatmap, target_class.item()))
    return images

def analyse_thread(yolo_path, classifier_path, grad_target_layer, tasks, results, device):
    yolo_model = YOLO(yolo_path, verbose=False).to(device)
    classifier = YOLO(classifier_path, verbose=False).to(device)
    # grad_cam = GradCam(classifier, classifier._modules[grad_target_layer])

    img_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    
    while True:
        for task_id, task in tasks.items():
            if task['state'] == 'PENDING':
                img = cv2.imread(task['image'])
                # result_images = analyse_and_classify(yolo_model, grad_cam, img_transform, img)
                result_images = analyse_and_classify_yolo(yolo_model, classifier, img)
                results[task_id] = {}
                results[task_id]['state'] = 'SUCCESS'
                results[task_id]['images'] = result_images
                tasks[task_id]['state'] = 'SUCCESS'
        time.sleep(1)