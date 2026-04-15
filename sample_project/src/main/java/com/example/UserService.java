package com.example;

public class UserService {

    private String name;
    /**
     * Busca un usuario por su identificador.
     *
     * @param id identificador único del usuario
     * @return el nombre del usuario encontrado
     */
    public String findUser(String id) {
        if (id == null || id.isEmpty()) {
            return "unknown";
        }
        return "user-" + id;
    }

    /**
     * Normaliza un valor textual.
     *
     * @param value texto de entrada
     * @return texto normalizado
     */
    private String normalize(String value) {
        return value == null ? "" : value.trim().toLowerCase();
    }

    public void ping() {
        System.out.println("pong");
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}