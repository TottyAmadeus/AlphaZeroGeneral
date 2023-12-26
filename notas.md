# Testes de Modelos

## Modelo 1 | GoTesteMax10moves

Formato:

- 'num_iterations': 4
- 'num_selfPlay_iterations': 20
- 'max_moves': 10
- 'num_mcts_searches': 15
- 'num_epochs': 4
- 'batch_size': 4

Não joga muito bem como esperado, foi só um teste para ver se um treino pequeno dava yield a alguma coisa funcional. Foi treinado sem saber que jogadas eram válidas.

## Modelo 2 | Go20_20_20_50_20_2

Formato: 20 20 20 50 20 2

- 'num_iterations': 20
- 'num_selfPlay_iterations': 30
- 'max_moves': 40
- 'num_mcts_searches': 100
- 'num_epochs': 200
- 'batch_size': 64

Depois de optimizar o código, o self-play ficou ~= 10x mais rápido, adicionei aos dados de treino as variantes de simetria e translação (8x mais dados). Depois do treino, o modelo prefere dar skip 9 em 10 vezes, deplorável. Após teste, corrigi erros na função de captura e na verificação de capturas, e melhorei a função que retorna quem ganhou. Os próximos treinos não terão limite de jogadas nas simulações de MCTS.

## Modelo 3 | Go20_10_100_200_8

- 'num_iterations': 20
- 'num_selfPlay_iterations': 10
- 'num_mcts_searches': 100
- 'num_epochs': 200
- 'batch_size': 8

## Modelo 4 | Go20_10_200_64

- 'num_iterations': 20
- 'num_selfPlay_iterations': 10
- 'num_mcts_searches': 100
- 'num_epochs': 200
- 'batch_size': 8

O modelo rapidamente converge para dar skip sempre, implementei finalmente a regra que se ambos skipparem, o jogo acaba, para ver se isto não acontece. Melhor modelo foi o primeiro mesmo...
