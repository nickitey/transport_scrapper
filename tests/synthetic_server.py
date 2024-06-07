from flask import Flask, render_template, request


app = Flask(__name__)
app.static_folder = 'templates/static/Секретаријат за јавни превоз _ Ред вожње_files'


@app.route('/linije/red-voznje/')
def render_main_page():
    return render_template('Секретаријат за јавни превоз _ Ред вожње.html')


@app.route('/linije/red-voznje/linija/2/prikaz')
def render_line_2():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 2.html')


@app.route('/linije/red-voznje/linija/18/prikaz')
def render_line_18():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 18.html')


@app.route('/linije/red-voznje/linija/10021/prikaz')
def render_line_21a():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 21A.html')


@app.route('/linije/red-voznje/linija/23/prikaz')
def render_line_23():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 23.html')


@app.route('/linije/red-voznje/linija/400/prikaz')
def render_line_400():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 400.html')


@app.route('/linije/red-voznje/linija/60314/prikaz')
def render_line_451a():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 451а.html')


@app.route('/linije/red-voznje/linija/60243/prikaz')
def render_line_460a():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 460а.html')


@app.route('/linije/red-voznje/linija/60249/prikaz')
def render_line_465():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 465.html')


@app.route('/linije/red-voznje/linija/60260/prikaz')
def render_line_493():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 493.html')


@app.route('/linije/red-voznje/linija/60271/prikaz')
def render_line_581a():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 581а.html')


@app.route('/linije/red-voznje/linija/60192/prikaz')
def render_line_4404a():
    return render_template('Секретаријат за јавни превоз _ Ред вожње линија 4404а.html')


if __name__ == '__main__':
    app.run(debug=True)
