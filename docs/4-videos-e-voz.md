# 4. Vídeos e voz (ElevenLabs)

## Voz padrão do Cleisson
- **Use sempre:** voz **"Cleissoniphone"** · `voice_id: 7QFeaHC6BUn8pfzCX0va` (gravada pelo iPhone, aprovada pelo Cleisson em 24/11/2026).
- **Não use:** "cleissonvoz" (`W33UPY7iGTMZyuAyUfXB`), que ficou aguda e com som de microfone ruim.
- Configuração aprovada: modelo `eleven_v4`, `language_code: pt`, `stability 0.5`, `similarity_boost 0.75`, `style 0`, `use_speaker_boost true`.
- Formato no plano Starter: `mp3_44100_128` (192 kbps só no plano Creator).
- A chave da API fica guardada no ambiente do Claude Code (Network secret do host `api.elevenlabs.io`, header `xi-api-key`). **Nunca** coloque a chave em código, chat ou repositório.
- Para legendas sincronizadas, use `POST /v1/text-to-speech/{voice_id}/with-timestamps`, que devolve o tempo de cada letra.

## Estilo dos vídeos (o que o Cleisson aprovou e o que ele recusou)
- **Recusado:** mascote de desenho e visual infantil, voz de robô e texto fraco.
- **Aprovado:** visual sério e escuro, telas reais do sistema, cursor clicando, legendas grandes palavra por palavra e trilha discreta que abaixa quando ele fala.
- Formato Reels 1080x1920. Deixe livres os ~250 px do topo e os ~400 px de baixo (botões do Instagram).
- Ao postar: ativar o **Rótulo de IA** do Instagram (a voz é gerada por IA).

## Público e mensagem
- Vídeos para **outros donos de assistência**: o sistema é **gratuito**, sem cobrança nenhuma (nem pela instalação).
- Versão divulgada: **versão local** (abre o link, cadastra a loja e usa; os dados ficam no aparelho). Link na bio do Instagram.
- O Cleisson é de **São Luís - MA**, com sotaque maranhense. Ele é músico e percebe diferença de tom e timbre.
