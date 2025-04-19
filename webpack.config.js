const path = require('path');

module.exports = {
    entry: {
        accounts: './saga/static/accounts/js/main.js',
    },
    output: {
        path: path.resolve(__dirname, 'saga/static/accounts/dist'),
        filename: '[name].bundle.js',
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js'],
        alias: {
            '@': path.resolve(__dirname, 'saga/static/accounts/js')
        }
    },
    devtool: 'source-map',
    mode: process.env.NODE_ENV === 'production' ? 'production' : 'development'
}; 