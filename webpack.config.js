const path = require('path');

module.exports = {
  entry: './static/js/main.js', // Point d'entrée principal
  output: {
    path: path.resolve(__dirname, 'staticfiles'),
    filename: 'bundle.js',
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.css'],
  },
  mode: 'production',
};
