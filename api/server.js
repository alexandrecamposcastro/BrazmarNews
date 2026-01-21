const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const cron = require('node-cron');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, 'public')));

// API para atualizar notícias manualmente
app.get('/api/update-news', (req, res) => {
    exec('python bot.py', { cwd: __dirname }, (error, stdout, stderr) => {
        if (error) {
            console.error(`Erro: ${error}`);
            return res.status(500).json({ 
                success: false, 
                error: stderr || error.message 
            });
        }
        
        console.log(`Saída: ${stdout}`);
        
        // Verificar se o arquivo foi criado
        const newsPath = path.join(__dirname, 'public', 'noticias.json');
        if (fs.existsSync(newsPath)) {
            const stats = fs.statSync(newsPath);
            res.json({
                success: true,
                message: 'Notícias atualizadas com sucesso!',
                lastUpdate: stats.mtime,
                output: stdout
            });
        } else {
            res.status(500).json({
                success: false,
                error: 'Arquivo noticias.json não foi criado'
            });
        }
    });
});

// API para verificar status
app.get('/api/status', (req, res) => {
    const newsPath = path.join(__dirname, 'public', 'noticias.json');
    
    if (fs.existsSync(newsPath)) {
        const stats = fs.statSync(newsPath);
        const data = JSON.parse(fs.readFileSync(newsPath, 'utf8'));
        
        res.json({
            status: 'online',
            lastUpdate: stats.mtime,
            newsCount: data.length,
            fileSize: stats.size
        });
    } else {
        res.json({
            status: 'no-data',
            message: 'Arquivo noticias.json não encontrado'
        });
    }
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Agendar atualização automática a cada 4 horas
if (process.env.NODE_ENV === 'production') {
    cron.schedule('0 */4 * * *', () => {
        console.log('Executando atualização automática das notícias...');
        exec('python bot.py', { cwd: __dirname }, (error, stdout, stderr) => {
            if (error) {
                console.error('Erro na atualização automática:', error);
            } else {
                console.log('Atualização automática concluída:', stdout);
            }
        });
    });
    console.log('Agendador de atualizações ativado (a cada 4 horas)');
}

app.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
    console.log(`Modo: ${process.env.NODE_ENV || 'development'}`);
});