from serve import app
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PyHacc http view')
    parser.add_argument('--conn', type=str, default='sqlite://', help='connection string sqlalchemy style')
    args = parser.parse_args()

    app.conn = args.conn

    app.run(host='0.0.0.0', debug=True)
