import pygame as p
import ChessEngine, ChessAI
import sys


BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQUARE_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}




def loadImages():
    # Hàm khởi tạo thư viện ảnh
    # Hàm này được gọi duy nhất 1 lần trong main
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQUARE_SIZE, SQUARE_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT+30))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    game_state = ChessEngine.GameState()
    valid_moves = game_state.getValidMoves()
    move_made = False  # đánh dấu đã thực hiện nước đi hay chưa
    animate = False  # đánh dấu có thực hiện hoạt ảnh hay không
    loadImages()  # thực hiện 1 lần duy nhất để load ảnh các quân cờ
    running = True
    square_selected = ()  # lưu ô cuối mà người chơi click    ex: (4,5)
    player_clicks = []  # lưu 2 ô cuối mà người chơi click    ex: [(2,4),(2,5)]
    game_over = False
    move_undone = False
    move_log_font = p.font.SysFont("Arial", 14, False, False)
    node = 0
    evaluation = 0
    player_one = True  # người chơi quân trắng
    player_two = False  # người chơi quân đen

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            # điều khiển chuột
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) tọa độ của chuột
                    col = location[0] // SQUARE_SIZE
                    row = location[1] // SQUARE_SIZE
                    if square_selected == (row, col) or col >= 8:  # người chơi đã ấn 2 lần vào 1 ô hoặc ấn ra ngoài thì sẽ làm lại
                        square_selected = ()  # Coi như chưa chọn gì
                        player_clicks = []  # Xóa lịch sử click
                    else:
                        square_selected = (row, col)
                        player_clicks.append(square_selected) # thêm click vào danh sách
                    if len(player_clicks) == 2 and human_turn:  # ấn lần 2
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)): # xét các nước đi hợp lệ
                            if move == valid_moves[i]: # nếu nước đi hợp lệ thì đi
                                game_state.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()  # reset click của người chơi
                                player_clicks = []
                        if not move_made: # nếu chưa đi được thì coi như lần ấn đầu tiên là vào square_selected
                            player_clicks = [square_selected]

            # điều khiển phím
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # ấn z để undo
                    game_state.undoMove()
                    move_made = True
                    animate = False
                    game_over = False
                    move_undone = True
                if e.key == p.K_r:  # ấn r để reset game
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.getValidMoves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    move_undone = True

        # tìm kiếm nước đi của AI
        if not game_over and not human_turn and not move_undone:
            ai_move = ChessAI.findBestMoveAlphaBeta(game_state,valid_moves)
            node = ChessAI.number_of_nodes
            if ai_move != None:
                game_state.makeMove(ai_move)
            else :
                game_state.makeMove(ChessAI.findRandomMove(valid_moves))
            move_made = True
            animate = True

        if move_made:
            if animate:
                animateMove(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.getValidMoves()
            move_made = False
            animate = False
            move_undone = False

        evaluation = ChessAI.scoreBoard(game_state)
        drawGameState(screen, game_state, valid_moves, square_selected, node, evaluation)

        if not game_over:
            drawMoveLog(screen, game_state, move_log_font)

        if game_state.checkmate:
            game_over = True
            if game_state.white_to_move:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_over = True
            drawEndGameText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, game_state, valid_moves, square_selected, node,evaluation):
    # hàm vẽ trạng thái bàn cờ hiện tại bao gồm bàn cờ, các nước đi hợp lệ, thanh lợi thế (evaluation_bar)
    drawBoard(screen)  # vẽ bàn cờ
    highlightSquares(screen, game_state, valid_moves, square_selected) # đánh dấu (đổi màu ô)
    drawPieces(screen, game_state.board)  # vẽ các quân cờ
    draw_evaluation_bar(screen, evaluation) # vẽ thanh lợi thế
    draw_information(screen, node)


def drawBoard(screen):
    # hàm vẽ bàn cờ 8x8
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def highlightSquares(screen, game_state, valid_moves, square_selected):
    # đánh dấu ô được chọn và các nước đi hợp lệ của quân cờ đó
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_col * SQUARE_SIZE, last_move.end_row * SQUARE_SIZE))
    if square_selected != ():
        row, col = square_selected
        if game_state.board[row][col][0] == ('w' if game_state.white_to_move else 'b'):
            # đánh dấu ô được chọn
            s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)  # độ trong suốt 0->255
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            # đánh dấu các nước đi hợp lệ của quân cờ được chọn
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))


def drawPieces(screen, board):
    # vẽ các quân cờ ở trạng thái bàn cờ hiện tại
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def drawMoveLog(screen, game_state, font):
    # vẽ bảng danh sách các nước đã đi của trận đấu
    move_log_rect = p.Rect(BOARD_WIDTH+1, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT-100)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def drawEndGameText(screen, text):
    # vẽ dòng chữ kết thúc game
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


def animateMove(move, screen, board, clock):
    # biểu diễn hoạt ảnh của nước đi
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_enpassant_move:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQUARE_SIZE, enpassant_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        p.display.flip()
        clock.tick(60)

def draw_evaluation_bar(screen, evaluation):
    # hàm vẽ thanh lợi thế
    eva = evaluation
    eva = round(eva , 2)
    tmp = eva
    if eva > 4:
        eva = 4 + (eva-4)/ 20
    if eva < -4:
        eva = -4 + (eva+4)/ 20
    h = BOARD_WIDTH//2 + eva*BOARD_WIDTH//10
    p.draw.rect(screen, p.Color("white"), p.Rect(0, BOARD_HEIGHT, BOARD_WIDTH, 50))
    p.draw.rect(screen, p.Color("black"), p.Rect(h,BOARD_HEIGHT,BOARD_WIDTH-h,50))
    if eva >= 0:
        font = p.font.SysFont("Helvitca", 20, True, False)
        textObject = font.render('+'+str(tmp), 0, p.Color('Black'))
        textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT+30).move(h//2 - textObject.get_width() / 2,
                                                         BOARD_HEIGHT + 15 - textObject.get_height() / 2)
        screen.blit(textObject, textLocation)
    if eva < 0:
        font = p.font.SysFont("Helvitca", 20, True, False)
        textObject = font.render('-' + str(tmp), 0, p.Color('White'))
        textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT + 30).move(h + (BOARD_WIDTH-h)//2 - textObject.get_width() / 2,
                                                             BOARD_HEIGHT + 15 - textObject.get_height() / 2)
        screen.blit(textObject, textLocation)

def draw_information(screen, node):
    p.draw.rect(screen, p.Color("white"), p.Rect(512,400,250,150))
    font = p.font.SysFont("Noto Sans", 25, False, False)
    textObject = font.render('DEPTH :' + str(ChessAI.DEPTH), 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT + 30).move(512+120 - textObject.get_width() / 2,
                                                                     BOARD_HEIGHT - 60 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

    font = p.font.SysFont("Noto Sans", 25, False, False)
    textObject = font.render('Nodes :' + str(node), 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT + 30).move(512 + 120 - textObject.get_width() / 2,
                                                                     BOARD_HEIGHT - 30 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)

if __name__ == "__main__":
    main()
