# import cv2
# import os
# import face_alignment
# import numpy as np
# from django.conf import settings
# import torch
# import numpy as np
# from PIL import Image
# from torchvision.transforms import ToTensor, Resize, RandomCrop,Compose,RandomHorizontalFlip,RandomVerticalFlip,ColorJitter
# import random
# import torchvision.transforms.functional as tf
# from ai_model import Prototype,Classifier,ResNet18,cnn1d,VGG,Regressor,TemporalConvNet
# from scipy.io import wavfile
# from scipy.io.wavfile import write
# import moviepy.editor as mp
# import scipy.io.wavfile as wav
# from python_speech_features import mfcc


# os.environ["CUDA_VISIBLE_DEVICES"] = "6"
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._3D, flip_input=False,device="cuda")

# def is_iou(x1,x2,y1,y2,x1_pre,x2_pre,y1_pre,y2_pre):
#     xs=[x1_pre,x2_pre]
#     ys=[y1_pre,y2_pre]
#     for x in xs:
#         for y in ys:
#             if x>=x1 and x<=x2 and y>=y1 and y<=y2:
#                 return True
#     xs=[x1,x2]
#     ys=[y1,y2]
#     for x in xs:
#         for y in ys:
#             if x>=x1_pre and x<=x2_pre and y>=y1_pre and y<=y2_pre:
#                 return True
#     return False

# def face_points_detect(img,x1_pre,x2_pre,y1_pre,y2_pre):
    
#     img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
#     img_h=img.shape[0]
#     img_w=img.shape[1]
#     faces = fa.get_landmarks(img)
#     if faces==None:
#         return None,None,None,x1_pre,x2_pre,y1_pre,y2_pre

#     x1,x2,y1,y2=0,0,0,0
#     maxn=0
#     pos=None
#     for face in faces:
#         xx1=int(np.min(face[:,0]))
#         xx2=int(np.max(face[:,0]))
#         yy1=int(np.min(face[:,1]))
#         yy2=int(np.max(face[:,1]))
#         w=xx2-xx1
#         h=yy2-yy1
#         if h*w>maxn:
#             x1,x2,y1,y2=xx1,xx2,yy1,yy2
#             maxn=h*w
#             pos=face
#             if w<h:
#                 cha=(h-w)//2
#                 x1=max(x1-cha,0)
#                 x2=min(x2+cha,img_w)
#             else:
#                 cha=(w-h)//2
#                 y1=max(y1-cha,0)
#                 y2=min(y2+cha,img_h)

#     if not ((x1_pre,x2_pre,y1_pre,y2_pre)==(0,0,0,0) or is_iou(x1,x2,y1,y2,x1_pre,x2_pre,y1_pre,y2_pre)):
#         return None,None,None,x1_pre,x2_pre,y1_pre,y2_pre
    
#     face_img=img.copy()[y1:y2,x1:x2]

#     no_lines=[16,21,26,30,35,41,47,60,67]
#     loop_lines=[(36,41),(42,47),(48,60),(61,67)]
#     for i in range(len(pos)):
#         cv2.circle(img,(int(pos[i][0]),int(pos[i][1])),1,(225,0,0))
#         if i not in no_lines:
#             cv2.line(img,(int(pos[i][0]),int(pos[i][1])),(int(pos[i+1][0]),int(pos[i+1][1])),(0,255,0),1)
#     for loop in loop_lines:
#         cv2.line(img,(int(pos[loop[0]][0]),int(pos[loop[0]][1])),(int(pos[loop[1]][0]),int(pos[loop[1]][1])),(0,255,0),1)
#     cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,0),2)

#     return img,face_img,pos,x1,x2,y1,y2

# def mp42img(dir_path):
#     checkpoint = torch.load(os.path.join(settings.BASE_DIR, 'ai/ai_model/face_tcn_frozen_v3.t7'))
#     net2 = VGG("VGG19")
#     net2.load_state_dict(checkpoint['net2'])
#     net2 = net2.to(device)
#     net3 = Regressor(512,64)
#     net3.load_state_dict(checkpoint['net3'])
#     net3 = net3.to(device) 
#     net2.eval()
#     net3.eval()

#     frame_score_list=[]
#     frame_fea_list=[]
#     video_name=dir_path.split('/')[-1]
#     cap = cv2.VideoCapture(dir_path)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#     frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#     print(frame_width,frame_height)
#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     tmp_save=os.path.join(settings.BASE_DIR,'ai/ai_feature/video_tmp.mp4')
#     out_save=os.path.join(settings.MEDIA_ROOT,'face_mp4/'+video_name)
#     out = cv2.VideoWriter(tmp_save,fourcc=fourcc, fps=fps, frameSize=(int(frame_width),int(frame_height)))
#     x1,x2,y1,y2=0,0,0,0
#     cnt=0
#     act_cnt=0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         img,face_img,pos,x1,x2,y1,y2=face_points_detect(frame,x1,x2,y1,y2)
#         if face_img is None or face_img.shape[0]*face_img.shape[1]*face_img.shape[2]==0:
#             continue    
#         act_cnt+=1
#         img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
#         face_img=cv2.cvtColor(face_img,cv2.COLOR_RGB2BGR)
#         out.write(img)
#         if act_cnt%(round(fps))==0:
#             cv2.imwrite(os.path.join(settings.BASE_DIR,'ai/ai_feature/face_tmp.jpg'),face_img) 
#             x=load_img()

#             with torch.no_grad():
#                 x = x.to(device)
#                 x = net2(x)
#                 score,fea = net3(x)
#                 score=float(score.cpu())
                
#                 frame_score_list.append(score)
#                 frame_fea_list.append(fea)

#             cnt+=1
#     cap.release() 
#     out.release()
#     os.system("ffmpeg -i "+tmp_save+" -vcodec libx264 -f mp4 "+out_save)
#     return frame_score_list,frame_fea_list,'face_mp4/'+video_name
        
# def load_img():
#     img = Image.open(os.path.join(settings.BASE_DIR,'ai/ai_feature/face_tmp.jpg')).convert('L')
#     img=np.array(img)
#     img = img[:, :, np.newaxis]
#     img = np.concatenate((img, img, img), axis=2)
#     img = Image.fromarray(img)
#     transform = Compose([Resize([48,48]),ToTensor()])
#     img=transform(img)
#     img=img.unsqueeze(0)
#     return img

# def mp42score(frame_fea_list):
#     tcn_num=32
#     checkpoint = torch.load(os.path.join(settings.BASE_DIR, 'ai/ai_model/face_tcn_frozen_v3.t7'))
#     net4=TemporalConvNet(tcn_num,[32,16,16,1])
#     net4.load_state_dict(checkpoint['net4'])
#     net4 = net4.to(device)
#     net5 = Regressor(64,32)
#     net5.load_state_dict(checkpoint['net5'])
#     net5 = net5.to(device)
#     net4.eval()
#     net5.eval()

#     i=0
#     LEN=len(frame_fea_list)
    
#     items=[]
#     while i<LEN:
#         item=[]
#         choose_num=[x for x in range(i,i+min(tcn_num,LEN-i))]
#         if (LEN-i)<tcn_num:
#             for _ in range(tcn_num-(LEN-i)):
#                 randint=random.randint(i,LEN-1)
#                 choose_num.append(randint)
#             choose_num.sort()

#         for k in choose_num:
#             item.append(frame_fea_list[k])
#         items.append(item)

#         i+=tcn_num

#     outputs=0.0
#     for item in items:
#         with torch.no_grad():
#             feas=torch.stack(item)
#             feas=feas.squeeze(1).unsqueeze(0)
#             feas = net4(feas).squeeze(1)
#             output,_=net5(feas)
#             outputs+=float(output.cpu())
#     outputs/=len(items)
#     return outputs

# def score2npy(score_list,video_path,title):
#     npy_name=video_path.split('/')[-1]
#     npy_name=npy_name.split('.')[0]+'.npy'
#     dataset_savepath=os.path.join(title,npy_name)
#     out_save=os.path.join(settings.MEDIA_ROOT,dataset_savepath)
#     np.save(out_save,np.array(score_list))
    
#     return dataset_savepath

# def mp42wav(dir_path):
    
#     net2 = torch.load(os.path.join(settings.BASE_DIR, 'ai/ai_model/CNN.ckpt'))
#     net2 = net2.to(device)
#     net2.eval()

#     my_clip = mp.VideoFileClip(dir_path)
#     wav_path=os.path.join(settings.BASE_DIR,'ai/ai_feature/voice_tmp.wav')
#     my_clip.audio.write_audiofile(wav_path)
#     (rate,sig) = wav.read(wav_path)
#     sig=sig[:,0]
#     scores,feas=[],[]
#     for i in range(len(sig)//100000):
#         npy = mfcc(sig[i*100000:(i+1)*100000],rate,nfft=1103)
#         npy = npy[0:199, :]
#         npy=torch.from_numpy(npy)
#         npy=torch.unsqueeze(npy, 0)
#         npy=torch.unsqueeze(npy, 0)
#         x=npy.to(torch.float32)
        
#         with torch.no_grad():
#             x = x.to(device)
#             score,fea = net2(x)
#             score=score.cpu()
#             pscore=np.exp(score[0][1])/(np.exp(score[0][0])+np.exp(score[0][1]))
#             pscore=float(pscore)
#             feas.append(fea)
#             scores.append(pscore)
#     return scores,feas

# def wav2score(voice_score_list):
#     tcn_num=32
#     checkpoint = torch.load(os.path.join(settings.BASE_DIR, 'ai/ai_model/voice_tcn_frozen.t7'))
#     net4=TemporalConvNet(tcn_num,[32,16,16,1])
#     net4.load_state_dict(checkpoint['net4'])
#     net4 = net4.to(device)

#     net5 = Regressor(2048,2048//2)
#     net5.load_state_dict(checkpoint['net5'])
#     net5 = net5.to(device)
#     net4.eval()
#     net5.eval()

#     i=0
#     LEN=len(voice_score_list)
    
#     items=[]
#     while i<LEN:
#         item=[]
#         choose_num=[x for x in range(i,i+min(tcn_num,LEN-i))]
#         if (LEN-i)<tcn_num:
#             for _ in range(tcn_num-(LEN-i)):
#                 randint=random.randint(i,LEN-1)
#                 choose_num.append(randint)
#             choose_num.sort()

#         for k in choose_num:
#             item.append(voice_score_list[k])
#         items.append(item)

#         i+=tcn_num

#     outputs=0.0
#     for item in items:
#         with torch.no_grad():
#             feas=torch.stack(item)
#             feas=feas.squeeze(1).unsqueeze(0)
#             feas = net4(feas).squeeze(1)
#             output,_=net5(feas)
#             outputs+=float(output.cpu())
#     outputs/=len(items)
#     return outputs

# def ai_main(video_path):
#     voice_score_list,voice_fea_list=mp42wav(video_path)
#     voice_score=wav2score(voice_fea_list)
#     voice_score_npy_path=score2npy(voice_score_list,video_path,'voice_score_npy')

#     frame_score_list,frame_fea_list,face_mp4_path=mp42img(video_path)
#     face_score=mp42score(frame_fea_list)
#     face_score_npy_path=score2npy(frame_score_list,video_path,'face_score_npy')
    
#     return face_score,face_mp4_path,face_score_npy_path,voice_score,voice_score_npy_path
    

