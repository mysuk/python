import pyautogui as m
import keyboard
import pygame
from time import sleep

pygame.init() # 초기화 (반드시 필요)

# 화면 크기 설정
screen_width = 350 # 가로 크기
screen_height = 200 # 세로 크기
screen = pygame.display.set_mode((screen_width,screen_height))

# 화면 타이틀 설정
pygame.display.set_caption("마우스 무빙")

# 폰트 로딩 및 텍스트 객체 초기화
fontObj = pygame.font.Font('C:\\Windows\\Fonts\\malgunbd.ttf', 24)
textSurfaceObj1 = fontObj.render("화면을 클릭하면 마우스 무빙.", True, (255, 255, 255))
textRectObj1 = textSurfaceObj1.get_rect();
textRectObj1.center = (180, 100)

textSurfaceObj2 = fontObj.render("x를 누르면 화면 종료.", True, (255, 255, 255))
textRectObj2 = textSurfaceObj2.get_rect();
textRectObj2.center = (180, 150)

# 이벤트 루프
running = True # 진행중인가?
i = 0
mouse_xpos = 0
mouse_ypos = 0
flg = False
while running:
    for event in pygame.event.get(): # 어떤 이벤트가 발생하였는가?
        if event.type == pygame.QUIT: # 창이 닫히는 이벤트가 발생하였는가?
            running = False # 진행중이 아님
        
        if event.type == pygame.KEYDOWN: # 키가 눌러졌는지 확인
            if event.key == pygame.K_x: # 캐릭터를 왼쪽으로
                print('마우스 멈춤')
                running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_xpos = m.position().x
            mouse_ypos = m.position().y
            if flg == False:
                flg = True
            else:
                flg = False

    if(i%2 == 0 and flg):
        i = 1
        if keyboard.is_pressed('x'):
            print('마우스 멈춤1')
            running = False
        m.moveTo(mouse_xpos+100,mouse_ypos,1)
        # sleep(60*8)
        if keyboard.is_pressed('x'):
            print('마우스 멈춤2')
            running = False
    elif(flg):   
        i = 2     
        if keyboard.is_pressed('x'):
            print('마우스 멈춤3')
            running = False
        m.moveTo(mouse_xpos,mouse_ypos,1)
        # sleep(60*8)
        if keyboard.is_pressed('x'):
            print('마우스 멈춤4')
            running = False
        
    # 텍스트 오브젝트를 출력
    screen.blit(textSurfaceObj1, textRectObj1)
    screen.blit(textSurfaceObj2, textRectObj2)
    pygame.display.update() # 게임화면을 다시 그리기

# pygame 종료
pygame.quit()
