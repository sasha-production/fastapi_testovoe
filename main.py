import fastapi
import uvicorn
import json
import typing
from fastapi import Path, status
from fastapi.responses import JSONResponse

app = fastapi.FastAPI()


def get_comments_count_by_id(news_id: int) -> int:
    with open('comments.json', encoding='utf-8') as file:
        comments_array = json.load(file).get('comments')
        comments_count = 0
        for comment_info in comments_array:
            if comment_info['news_id'] == news_id:
                comments_count += 1
        return comments_count


def get_comments_by_id(news_id) -> list:
    with open('comments.json', encoding='utf-8') as file:
        comments_array = json.load(file).get('comments')
    comments_by_id_array = []
    for i in range(len(comments_array)):
        if comments_array[i]['news_id'] == news_id:
            comments_by_id_array.append(comments_array[i])
    return comments_by_id_array


@app.get('/')
async def get_all_news():
    with open('news.json', encoding='utf-8') as file:
        news_data = json.load(file)

    news_count = len(news_data.get('news'))
    for i in range(news_count):
        if not news_data['news'][i]['deleted']:  ## возвращать необходимо не удаленные записи (поле "deleted")
            news_id = news_data['news'][i]['id']
            news_comments = get_comments_count_by_id(news_id)
            news_data['news'][i]['comments_count'] = news_comments

    return JSONResponse(content=news_data, status_code=status.HTTP_200_OK)


@app.get('/news/{id}')
async def get_news_by_id(id: int = Path(ge=1)):
    with open('news.json', encoding='utf-8') as file:
        news_data = json.load(file)
    news_info = None
    for news in news_data.get('news'):
        if news['id'] == id:
            news_info = news
            break
    else:
        return JSONResponse(content="No such news", status_code=status.HTTP_404_NOT_FOUND)

    if news_info['deleted']:
        return JSONResponse(content="The news was deleted", status_code=status.HTTP_404_NOT_FOUND)
    comments_by_id = get_comments_by_id(news_info['id'])
    news_info['comments'] = comments_by_id
    news_info['comments_count'] = len(comments_by_id)
    return JSONResponse(content=news_info, status_code=status.HTTP_200_OK)


if __name__ == '__main__':
    uvicorn.run(app=app,
                host='127.0.0.1',
                port=8000,
                )
