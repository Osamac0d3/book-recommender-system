from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load data
popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

# Remove duplicates
books = books.drop_duplicates('Book-Title')
popular_df = popular_df.drop_duplicates('Book-Title')


@app.route('/')
def index():

    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values)
    )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend_books():

    user_input = request.form.get('user_input')

    if user_input not in pt.index:
        return render_template(
            'recommend.html',
            data=[],
            error="Book not found in database"
        )

    index = np.where(pt.index == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:10]

    data = []
    seen = set()

    for i in similar_items:

        title = pt.index[i[0]]

        if title in seen:
            continue

        seen.add(title)

        temp_df = books[books['Book-Title'] == title].drop_duplicates('Book-Title')

        if temp_df.empty:
            continue

        book_title = temp_df['Book-Title'].values[0]
        author = temp_df['Book-Author'].values[0]
        image = temp_df['Image-URL-M'].values[0]

        if book_title and author and image:
            data.append([book_title, author, image])

        if len(data) == 6:
            break

    return render_template('recommend.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)