import json
import logging
import pickle
import random
import re
import time
from io import BytesIO
import pickle
import matplotlib.pyplot as plt
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
#logger为什么无效？
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class Geetest(object):
    def __init__(self):
        with open(r'C:\Users\Administrator\Desktop\bilibili_danmu\location_list.pkl', 'rb') as f:
            self.location_list=pickle.load(f)
        #options = Options()
        #options.add_argument('-headless')  # 无头参数
        #self.driver=webdriver.Firefox(executable_path=r'D:\Program Files (x86)\Mozilla Firefox\geckodriver',firefox_options=options)
        self.driver=webdriver.Firefox(executable_path=r'D:\Program Files (x86)\Mozilla Firefox\geckodriver')
        self.driver.get('https://passport.bilibili.com/login')
        WebDriverWait(self.driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']").is_displayed())
        #WebDriverWait(self.driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_bg gt_show']").is_displayed())
        #WebDriverWait(self.driver, 30).until(lambda the_driver: the_driver.find_element_by_xpath("//div[@class='gt_cut_fullbg gt_show']").is_displayed())

    def get_bg_fullbg(self):
        '获取验证码的地址'
        html=self.driver.find_elements_by_class_name('gt_cut_fullbg_slice')[0].get_attribute('style')
        fullbg_picture=re.findall(r'url\(\"(.+)\"\)',html)[0]
        html=self.driver.find_elements_by_class_name('gt_cut_bg_slice')[0].get_attribute('style')
        bg_picture=re.findall(r'url\(\"(.+)\"\)',html)[0]
        fullbg_picture=Image.open(BytesIO((requests.get(fullbg_picture).content))) 
        bg_picture=Image.open(BytesIO((requests.get(bg_picture).content))) 
        return  fullbg_picture,bg_picture

    def get_merge_image(self,img):
        '将打乱的验证码拼为完整的图片'
        #打乱的验证码为大小312*116的图片，而完整的验证码为大小260*116的图片，这就需要在拼接的时候对原图进行裁剪
        new_img=Image.new('RGB',(260,116),(255,255,255))
        for i in range(51):
            name=str(i+1)+'bg'
            #取出原图的上部放入新图的下部
            if self.location_list[name]['y']==58:
                box1=(self.location_list[name]['x'],58,self.location_list[name]['x']+10,58+58)
                box2=(10*i,0,10*i+10,58)
            #取出原图的下部放入新图的上部
            else:
                box1=(self.location_list[name]['x'],0,self.location_list[name]['x']+10,58)
                box2=(10*(i-26),58,10*(i-26)+10,58+58)
            region=img.crop(box1)
            new_img.paste(region,box2)
        return new_img

    def get_gap(self,fullbg_picture,bg_picture,x,y):
        '找到验证码的缺口'
        threshold=50
        fullbg_pixel=fullbg_picture.getpixel((x,y))
        bg_pixel=bg_picture.getpixel((x,y))
        for i in range(3):
            if abs(fullbg_pixel[i]-bg_pixel[i])>threshold:
                return True
        return False

    def get_x_pos(self,fullbg_picture,bg_picture):
        '计算移动距离'
        width,height=fullbg_picture.size
        for i in range (width):
            for j in range (height):
                if self.get_gap(fullbg_picture,bg_picture,i,j):          
                    #注意slice中图片的最左侧的x像素值并不是0，而是6，因此需要减去这个值，以得到准确的移动距离
                    logger.debug ('距离为：%d'%(i-6)) 
                    return i-6

    def get_track(self,x_pos):
        '根据缺口位置计算移动轨迹'
        track_list=[]
        distance_list=[]
        current_pos,v,tt=0,0,0
        mid=x_pos*random.uniform(0.6,0.85)
        while current_pos-x_pos<0:
            if current_pos < mid:
                a = random.randint(20,25)/10
            else:	
                a = random.randint(-30,-20)/10
            t=random.randint(20,30)/100
            v0 = v
            v = v0 + a * t
            move = round(v0 * t + 1 / 2 * a * t * t)
            current_pos += move
            tt+=t/5
            track=[current_pos,tt]
            track_list.append(track)
            distance=[move,t/5]
            distance_list.append(distance)
        if track_list[-1][0]-x_pos>3:
            track_list.append([x_pos,track_list[-1][2]+random.uniform(0.1,0.2)])
            distance_list.append([x_pos-track_list[-1][0],distance_list[-1][2]+random.randint(10,20)/100])
        return distance_list 

    def simulate_move(self,distance_list):   
        slider_knob = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
        logger.debug ('验证中...')    
        # 点击滑块并按住不放
        ActionChains(self.driver).click_and_hold(on_element=slider_knob).perform()
        time.sleep(0.01)
        #拖动滑块
        for distance in distance_list:
            x_offset=distance[0]
            #xoffsethe yoffset须为整数
            ActionChains(self.driver).move_by_offset(xoffset=x_offset, yoffset=0).perform()    
            time.sleep(distance[1])  
            logger.debug(slider_knob.location['x'],slider_knob.location['y'])                            
        time.sleep(random.uniform(0.3, 0.8))    
        ActionChains(self.driver).release(on_element=slider_knob).perform()
        WebDriverWait(self.driver, 30).until(lambda the_driver: the_driver.find_element_by_class_name('gt_info_type').is_displayed())
        return self.driver.find_element_by_class_name('gt_info_type').text

    def crack(self):
        fullbg_picture,bg_picture=self.get_bg_fullbg()
        fullbg_picture=self.get_merge_image(fullbg_picture)
        bg_picture=self.get_merge_image(bg_picture)
        x_pos=self.get_x_pos(fullbg_picture,bg_picture)
        distance_list=self.get_track(x_pos)
        return self.simulate_move(distance_list)
        

    def login(self,username,password):
            login_username = self.driver.find_element_by_id("login-username")
            login_passwd = self.driver.find_element_by_id("login-passwd")
            #为什么网站上显示的是btn btn-login？
            btn_box = self.driver.find_element_by_class_name("btn.btn-login")
            login_username.send_keys(username)
            login_passwd.send_keys(password)
            flag_success = False
            while not flag_success:
                result=self.crack()
                if result==None:
                    #刷新页面
                    #self.driver.refresh()
                    logger.debug ('验证未通过') 
                #注意格式
                elif '验证失败' in result or '再来一次' in result:
                    time.sleep(5)
                    #self.driver.refresh()
                    logger.debug ('正在重试') 
                elif '验证通过' in result:
                    flag_success = True
                else:
                    logger.debug ('出现错误，退出') 
                    break
            if flag_success:
                logger.debug ('正在登陆...') 
                btn_box.click()
                time.sleep(5)
                cookie = self.driver.get_cookies()
                print(" ".join('%s' %id for id in cookie))
            #存储cookie
            with open(r'C:\Users\Administrator\Desktop\bilibili_danmu\cookie.pkl', 'wb') as f:
                pickle.dump(cookie,f)
                self.driver.quit()

if __name__=='__main__':
    geetest=Geetest()
    geetest.login('xxx','xxx')
