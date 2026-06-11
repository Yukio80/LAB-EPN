// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract QuadraticVote {
    address public admin;
    uint256 public custo_credito = 0.001 ether;

    struct Proposta {
        bytes32 hash_proposta;
        string titulo;
        uint256 votos_sim;
        uint256 votos_nao;
        uint256 total_creditos_sim;
        uint256 total_creditos_nao;
        bool ativa;
        uint256 deadline;
    }

    mapping(uint256 => Proposta) public propostas;
    mapping(uint256 => mapping(address => uint256)) public creditos_gastos;
    uint256 public contador_propostas;

    event VotoCast(uint256 indexed proposta_id, address indexed eleitor, bool voto, uint256 creditos);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Apenas admin");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function criarProposta(bytes32 _hash, string calldata _titulo, uint256 _duracao) external onlyAdmin {
        propostas[contador_propostas] = Proposta({
            hash_proposta: _hash,
            titulo: _titulo,
            votos_sim: 0,
            votos_nao: 0,
            total_creditos_sim: 0,
            total_creditos_nao: 0,
            ativa: true,
            deadline: block.timestamp + _duracao
        });
        contador_propostas++;
    }

    function votar(uint256 _proposta_id, bool _voto, uint256 _creditos) external payable {
        Proposta storage p = propostas[_proposta_id];
        require(p.ativa, "Proposta inativa");
        require(block.timestamp < p.deadline, "Votacao encerrada");
        require(_creditos > 0, "Creditos devem ser > 0");
        uint256 custo = _creditos * _creditos * custo_credito;
        require(msg.value >= custo, "Valor insuficiente");

        creditos_gastos[_proposta_id][msg.sender] += _creditos;

        if (_voto) {
            p.votos_sim += 1;
            p.total_creditos_sim += _creditos;
        } else {
            p.votos_nao += 1;
            p.total_creditos_nao += _creditos;
        }

        emit VotoCast(_proposta_id, msg.sender, _voto, _creditos);
    }

    function resultado(uint256 _proposta_id) external view returns (bool aprovada, uint256 votos_sim, uint256 votos_nao) {
        Proposta storage p = propostas[_proposta_id];
        return (p.total_creditos_sim > p.total_creditos_nao, p.votos_sim, p.votos_nao);
    }
}
