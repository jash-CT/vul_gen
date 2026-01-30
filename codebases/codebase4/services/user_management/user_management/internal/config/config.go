package config

import (
	"os"
	"strings"
)

type Config struct {
	DatabaseURL      string
	GRPCAddress      string
	JWTSecret        []byte
	AllowedProviders []string
	LogLevel         string
}

func LoadConfig() *Config {
	return &Config{
		DatabaseURL:      getEnv("DATABASE_URL", "postgres://user:pass@localhost/usermgmt"),
		GRPCAddress:      getEnv("GRPC_ADDRESS", ":50051"),
		JWTSecret:        []byte(getEnv("JWT_SECRET", "development-secret-please-change")),
		AllowedProviders: strings.Split(getEnv("ALLOWED_PROVIDERS", "local,ldap,oauth"), ","),
		LogLevel:         getEnv("LOG_LEVEL", "info"),
	}
}

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}